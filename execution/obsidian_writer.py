import os
import time
import logging

logger = logging.getLogger(__name__)

class ObsidianWriter:
    """
    代替 API Packager，负责将最终套利成果（翻译润色后的简报）
    硬写入本地 Obsidian Vault 文件夹，实现最终的变现闭环。
    """
    def __init__(self, vault_path: str = "./ObsidianVault"):
        self.vault_path = vault_path
        os.makedirs(self.vault_path, exist_ok=True)
        
    def write_daily_brief(self, node_id: str, title: str, pitch_script: str, tags: list[str], link: str):
        # 提取对操作系统文件命名合法的文件前缀名
        safe_title = "".join(x for x in title if x.isalnum() or x in " -_")[:60]
        date_str = time.strftime("%Y-%m-%d")
        
        filename = f"[{date_str}] {safe_title}.md"
        filepath = os.path.join(self.vault_path, filename)
        
        # 将结构洞返回的 tags 列表映射为 Obsidian 规范的 #Tag
        valid_tags = [str(t).replace(" ", "_").replace("-", "_") for t in tags]
        
        content = f"""---
id: {node_id}
date: {date_str}
tags: [{', '.join(valid_tags)}]
source: {link}
---

# {title}

## 📝 核心学术摘要 (AI Generated)
{pitch_script}

## 🔗 原文链接流
[点击溯源 arXiv 源站]({link})
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        logger.info(f"✅ Obsidian brief safely committed: {filepath}")
