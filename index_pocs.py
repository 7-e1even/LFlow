#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POC索引脚本 - 将YAML文件索引到Meilisearch"""

import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
import meilisearch

# Windows终端UTF-8支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加app目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.config import settings


def extract_urls(yaml_content: dict) -> tuple[list[str], list[str]]:
    """提取YAML中的URL路径和关键词
    
    Args:
        yaml_content: 解析后的YAML内容
        
    Returns:
        (urls列表, 关键词列表)
    """
    url_set = set()
    
    if 'http' in yaml_content and yaml_content['http']:
        for req in yaml_content['http']:
            # 提取path字段
            if 'path' in req and req['path']:
                paths = req['path'] if isinstance(req['path'], list) else [req['path']]
                for path in paths:
                    if path:
                        clean = re.sub(r'\{\{.*?\}\}', '', path.strip())
                        if clean and clean != '/':
                            url_set.add(clean)
            
            # 提取raw字段中的URL
            if 'raw' in req and req['raw']:
                for raw in req['raw']:
                    match = re.search(
                        r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)\s+HTTP', 
                        raw, 
                        re.IGNORECASE
                    )
                    if match:
                        clean = re.sub(r'\{\{.*?\}\}', '', match.group(2)).strip()
                        if clean and clean != '/':
                            url_set.add(clean)
    
    # 生成关键词
    urls = list(url_set)
    url_keywords = []
    for url in urls:
        base = url.split('?')[0]
        url_keywords.append(base)
        url_keywords.extend([s for s in base.split('/') if s])
    
    return urls, list(set(url_keywords))


def read_yaml_files(folder_path: str) -> list[dict]:
    """读取并解析YAML文件
    
    Args:
        folder_path: YAML文件夹路径
        
    Returns:
        POC文档列表
    """
    poc_data = []
    poc_id_set = set()
    duplicates = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ 错误: 文件夹不存在 - {folder_path}")
        return poc_data
    
    yaml_files = list(folder.rglob("*.yaml")) + list(folder.rglob("*.yml"))
    print(f"📁 找到 {len(yaml_files)} 个YAML文件\n")
    
    for idx, file in enumerate(yaml_files, 1):
        try:
            content = file.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
            
            if not data:
                continue
            
            poc_id = data.get('id', '')
            
            # 去重检查
            if poc_id and poc_id in poc_id_set:
                duplicates.append(file.name)
                print(f"[{idx}/{len(yaml_files)}] ⏭️  {file.name} - 跳过（重复）")
                continue
            
            # 提取URL
            urls, keywords = extract_urls(data)
            
            # 构建文档
            doc = {
                'id': poc_id or f"unnamed_{file.stem}",
                'poc_id': poc_id,
                'name': data.get('info', {}).get('name', ''),
                'author': data.get('info', {}).get('author', ''),
                'severity': data.get('info', {}).get('severity', ''),
                'description': data.get('info', {}).get('description', ''),
                'tags': data.get('info', {}).get('tags', ''),
                'urls': urls,
                'url_keywords': keywords,
                'yaml_content': content,
                'metadata': data.get('info', {}).get('metadata', {}),
                'indexed_at': datetime.now().isoformat()
            }
            
            poc_data.append(doc)
            if poc_id:
                poc_id_set.add(poc_id)
            
            print(f"[{idx}/{len(yaml_files)}] ✅ {file.name} - {len(urls)} URLs")
            
        except Exception as e:
            print(f"[{idx}/{len(yaml_files)}] ❌ 错误: {file.name} - {e}")
    
    if duplicates:
        print(f"\n⚠️  跳过 {len(duplicates)} 个重复POC")
    
    return poc_data


def upload_to_meilisearch(documents: list[dict]):
    """上传文档到Meilisearch
    
    Args:
        documents: POC文档列表
    """
    if not documents:
        print("\n⚠️  没有文档可上传")
        return
    
    try:
        client = meilisearch.Client(settings.meilisearch_url, settings.meilisearch_key)
        index = client.index(settings.index_name)
        
        print(f"\n📤 上传 {len(documents)} 个文档到索引 '{settings.index_name}'...")
        task = index.add_documents(documents, primary_key='id')
        
        # 配置索引
        index.update_searchable_attributes([
            'urls', 'url_keywords', 'poc_id', 'name', 'description', 'tags', 'author'
        ])
        index.update_filterable_attributes(['severity', 'author', 'tags', 'poc_id'])
        index.update_sortable_attributes(['indexed_at', 'severity'])
        index.update_ranking_rules([
            'words', 'typo', 'proximity', 'attribute', 'sort', 'exactness'
        ])
        
        task_uid = task.task_uid if hasattr(task, 'task_uid') else 'N/A'
        print(f"✅ 上传完成！任务ID: {task_uid}")
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("📚 Nuclei POC 索引工具")
    print("=" * 60)
    print(f"索引名称: {settings.index_name}")
    print(f"POC文件夹: {settings.poc_folder}\n")
    
    # 读取YAML文件
    poc_data = read_yaml_files(settings.poc_folder)
    
    if not poc_data:
        print("\n⚠️  没有找到有效的POC文件")
        return
    
    total_urls = sum(len(doc['urls']) for doc in poc_data)
    print(f"\n📊 统计: {len(poc_data)} 个POC, {total_urls} 个URL")
    
    # 上传到Meilisearch
    upload_to_meilisearch(poc_data)
    
    print("\n" + "=" * 60)
    print("🎉 索引完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

