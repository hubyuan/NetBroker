import ast
import logging

logger = logging.getLogger(__name__)

class AstSecurityScanner:
    """
    负责清扫抓取到的 Python 源码字符串，防止原生执行时受到毁灭性越权打击。
    阻断一切 subprocess、os.* 系统调用，不允许反射执行 (eval/exec)。
    摒弃笨重的 Docker 沙盒，改用超轻量级的「白名单/黑名单静态逻辑树」达到安全下限。
    """
    FORBIDDEN_NAMES = {"os", "subprocess", "sys", "eval", "exec", "open", "__import__", "socket"}

    @classmethod
    def is_safe_to_execute(cls, source_code: str) -> bool:
        """
        验证源代码片段是否含有恶意模块引入或危险系统级操作指令。
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            logger.error(f"Syntax error during AST parse (Cannot be natively trusted): {e}")
            return False

        for node in ast.walk(tree):
            # 检查直接的方法调用 (e.g. eval("print('hack')"))
            if isinstance(node, ast.Name):
                if node.id in cls.FORBIDDEN_NAMES:
                    logger.warning(f"AST Scanner blocked execution! Forbidden identifier found: {node.id}")
                    return False
            
            # 检查属性调用 (e.g. os.system())
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id in cls.FORBIDDEN_NAMES:
                        logger.warning(f"AST Scanner blocked execution! Forbidden module invocation: {node.value.id}.{node.attr}")
                        return False
                        
            # 检查直接导入包 (e.g. import subprocess)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in cls.FORBIDDEN_NAMES:
                        logger.warning(f"AST Scanner blocked execution! Forbidden module import: {alias.name}")
                        return False
                        
            # 检查 FROM 导入语法 (e.g. from os import system)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in cls.FORBIDDEN_NAMES:
                    logger.warning(f"AST Scanner blocked execution! Forbidden module importfrom: {node.module}")
                    return False

        return True
