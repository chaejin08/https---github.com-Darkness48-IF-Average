from common import gr, np, os
import time

class file_sink_10s(gr.sync_block):
    """
    300초 단위로 새로운 파일에 저장하고 평균 계산
    입력: float 벡터
    """
    def __init__(self, base_path="/home/chaejin/Downloads/dd/data", vec_len=8192):
        gr.sync_block.__init__(self,
            name="file_sink_300s",
            in_sig=[(np.float32, vec_len)],  # 벡터 길이 지정
            out_sig=None)

        self.base_path = base_path
        self.buffer = []
        self.start_time = time.time()
        self.file_index = 0
        self.vec_len = vec_len

    def work(self, input_items, output_items):
        data = input_items[0]
        self.buffer.extend(data.tolist())

        # 300초 경과 체크
        if time.time() - self.start_time >= 5:
            self.file_index += 1
            filename = f"{self.base_path}_{self.file_index:09d}.bin"
            np.array(self.buffer, dtype=np.float32).tofile(filename)

            print(f"Saved {filename}, samples={len(self.buffer)}")

            # 초기화
            self.buffer = []
            self.start_time = time.time()

        return len(data)