import re
import subprocess
from loguru import logger

class LwpSubprocess:

    LWP_PATH = "core/lwp.exe"

    err_map = {
        0: "OK",
        -1: "未知数据帧类型(CMD_UNKNOWN)",
        -2: "PL_LEN",
        -3: "MIC校验错误(MIC)",
        -4: "解密失败(DECRYPT)",
        -5: "未知Mac指令(MACCMD)",
        -6: "Mac指令数据长度错误(MACCMD_LEN)",
        -7: "Port0数据(FOPTS_PORT0)",
        -8: "入网请求长度错误(JOINR_LEN)",
        -9: "入网应答长度错误(JOINA_LEN)",
        -10: "MALLOC",
        -11: "NOT_AVALAIBLE",
        -12: "BAND",
        -13: "PAYLOAD长度为0(PARA)",
        -14: "NODE_USED_UP",
        -15: "未知数据格式(UNKOWN_FRAME)",
        -16: "TX_BUF_NOT_EMPTY",
        -17: "UNKOWN_DEVEUI",
        -18: "NO_HEAP",
        -19: "UNKOWN_DATA_RATE",
        -20: "FRAME_TOO_SHORT",
        -21: "NODE_EXISTS",
    }

    @staticmethod
    def run(cmd):
        ack = ""
        full_cmd = f"{LwpSubprocess.LWP_PATH} {cmd}"
        logger.debug(full_cmd)
        p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE)
        f = p.stdout
        while True:
            line = f.readline().decode("gb2312")
            if not line:
                break
            ack += line
        f.close()
        p.kill()

        match_obj = re.search(r"error\((-?\d+)\)", ack)
        if match_obj:
            ret = "Error: " + LwpSubprocess.err_map.get(int(match_obj.group(1)))
        else:
            ret = ack

        logger.debug(ret)
        return ret


class LwpCmd:

    @staticmethod
    def get_ver():
        return LwpSubprocess.run("-v")

    @staticmethod
    def parse_ul_maccmd(maccmd):
        return LwpSubprocess.run(f"-T UU -m {maccmd}")

    @staticmethod
    def parse_dl_maccmd(maccmd):
        return LwpSubprocess.run(f"-T UD -m {maccmd}")

    @staticmethod
    def parse_jr_ja(jr, ja, appkey):
        return LwpSubprocess.run(f"--join --jr {jr} --ja {ja} --appkey {appkey}")

    @staticmethod
    def parse_payload(payload, appskey, nwkskey):
        return LwpSubprocess.run(f"--parse {payload} --appskey {appskey} --nwkskey {nwkskey}")


if __name__ == '__main__':
    logger.debug(LwpCmd.get_ver())
    logger.debug(LwpCmd.parse_ul_maccmd("0307"))
    logger.debug(LwpCmd.parse_dl_maccmd("0D2F2A894FDF03000000700352D70201"))
    exit(0)
