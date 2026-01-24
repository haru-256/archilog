import sys

from loguru import logger

from configs import LOG_LEVEL


def setup_logger() -> None:
    """ロガーの初期設定を行います。

    デフォルトのロガー設定をリセットし、標準エラー出力にデバッグレベルでログを出力するように設定します。
    """
    # 一度デフォルトの設定を消してから再設定
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL)
