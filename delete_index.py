#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""删除Meilisearch索引"""

import sys
from pathlib import Path
import meilisearch

# Windows终端UTF-8支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加app目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.config import settings


def delete_index():
    """删除索引"""
    try:
        client = meilisearch.Client(settings.meilisearch_url, settings.meilisearch_key)
        
        print("=" * 60)
        print("🗑️  删除Meilisearch索引")
        print("=" * 60)
        print(f"索引名称: {settings.index_name}")
        print(f"Meilisearch: {settings.meilisearch_url}\n")
        
        # 确认操作
        confirm = input(f"⚠️  确定要删除索引 '{settings.index_name}' 吗？(yes/no): ")
        
        if confirm.lower() not in ['yes', 'y']:
            print("\n❌ 已取消删除操作")
            return
        
        # 执行删除
        task = client.index(settings.index_name).delete()
        
        print(f"\n✅ 索引删除任务已提交")
        print(f"任务ID: {task.task_uid if hasattr(task, 'task_uid') else 'N/A'}")
        print(f"状态: {task.status if hasattr(task, 'status') else 'N/A'}")
        print("\n索引将在后台删除完成")
        
    except Exception as e:
        error_msg = str(e).lower()
        if "index_not_found" in error_msg:
            print(f"\n⚠️  索引 '{settings.index_name}' 不存在")
        else:
            print(f"\n❌ 删除失败: {e}")


if __name__ == "__main__":
    delete_index()

