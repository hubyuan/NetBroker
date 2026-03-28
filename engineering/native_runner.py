import asyncio
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class NativeEngineRunner:
    """
    TDD 层核心要求：由于完全信任上层 AST 的剥离安全兜底机制，
    摒弃 Docker / 物理级别沙箱隔离的高额心智与硬件成本，在当前环境中直接执行原生断言评测！
    以此达到最大的事件循环吞吐极限以及业务反馈率。
    """
    
    @classmethod
    async def run_pytest_suite(cls, source_code: str, test_code: str) -> bool:
        """
        动态构建系统级临时运行目录隔离文件，植入待测核心脚本和自动生成的测试脚本并挂起运行 pytest。
        :return: bool (True 说明所有用例运行均通过绿色反馈)
        """
        # 利用 tempfile 模块动态构建随机上下文子目录防止并发测试相互干涉磁盘
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "target_module.py")
            test_path = os.path.join(tmpdir, "test_target.py")
            
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(source_code)
                
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)
            
            logger.debug(f"Native Process: Spin-up pytest execution across virtual workspace {tmpdir}...")
            
            try:
                # 依托 asyncio 创建隔离化子进程，防止因为 CPU 密集阻断大网关
                process = await asyncio.create_subprocess_exec(
                    "pytest", "test_target.py",
                    cwd=tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # 限流阻塞直至 subprocess 反馈，配置时移
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20.0)
                
                if process.returncode == 0:
                    logger.info("✅ Code passed holistic native evaluation.")
                    return True
                else:
                    logger.warning(f"❌ Verification constraints snapped. Errors observed:\n{stdout.decode('utf-8', errors='ignore')[:300]}")
                    return False
                    
            except asyncio.TimeoutError:
                logger.error("Pytest execution timed out!")
                # 防止僵尸进程泄漏
                process.kill()
                return False
            except Exception as e:
                logger.error(f"Native Pytest suite crashed ungracefully: {e}")
                return False
