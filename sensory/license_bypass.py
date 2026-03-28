import re
from typing import Tuple

class LicenseBypassDecider:
    """
    负责执行「幻觉对撞裁决树」逻辑，配合 LLM 的合规判定使用。
    """
    
    # 静态安全许可协议的强匹配正则关键字
    SAFE_LICENSE_KEYWORDS = [
        r"MIT\s+License",
        r"Apache\s+License\s+2\.0",
        r"Permission\s+is\s+hereby\s+granted",
        r"BSD\s+[23]\-Clause"
    ]

    @classmethod
    def static_regex_scan(cls, license_text: str) -> bool:
        """
        Step 1: 扫描 README 或代码注释授权文本是否静态命中高频白名单。
        返回 True 表示极有可能是开源可商用。
        """
        if not license_text:
            return False
        
        for kw in cls.SAFE_LICENSE_KEYWORDS:
            if re.search(kw, license_text, flags=re.IGNORECASE):
                return True
        return False

    @classmethod
    def hallucination_bypass_decision(cls, regex_match: bool, llm_allow: bool) -> Tuple[bool, str]:
        """
        Step 3: 结合静态正则与 LLM 语义识别，执行幻觉绕过裁决。
        :return: (最终是否放行: bool, 裁决理由记录: str)
        """
        if llm_allow and regex_match:
            return True, "PASS: LLM AND Regex match."
        
        elif not llm_allow and regex_match:
            # 强制幻觉绕过 (Override Bypass)
            # 常出现在 LLM 过度谨慎、对免责条款（as-is, without warranty）判定失误时
            return True, "OVERRIDE BYPASS: LLM rejected but strict Regex matched safe keywords."
        
        elif llm_allow and not regex_match:
            # 拦截 (Block) - 防范 LLM 盲目乐观或者上下文理解丢失
            return False, "BLOCK: LLM allowed but Regex failed."
            
        else:
            # 静默销毁 (Destroy) - 都不满足直接返回套利不可行
            return False, "DESTROY: Both LLM and Regex rejected."
