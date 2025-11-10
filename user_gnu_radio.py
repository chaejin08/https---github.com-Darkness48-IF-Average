from common import os, qtgui, uhd, blocks, fft, window, gr, firdes, \
eng_float, intx, eng_notation, osmosdr, threading, sip

class please(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "please")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.vec = vec = 8192
        self.thro = thro = 250e3
        self.low = low = 1.418e6
        self.hydro = hydro = 1.42e9
        self.high = high = 1.422e9 

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_clock_source('external', 0)
        self.uhd_usrp_source_0.set_samp_rate(thro)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(hydro, 0)
        self.uhd_usrp_source_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_source_0.set_gain(0, 0)

        self.qtgui_sink_x_0 = qtgui.sink_c(
            vec, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            hydro, #fc
            thro, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/thro)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.fft_vxx_0 = fft.fft_vcc(vec, True, window.blackmanharris(8192), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(5, 1/5, 4000, 8192)
        
        os.makedirs("/home/chaejin/Downloads/dd", exist_ok=True)

        self.blocks_python_file_10s = file_sink_10s("/home/chaejin/Downloads/dd/back_correction")
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(vec)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_python_file_10s, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_sink_x_0, 0))




    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "please")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_vec(self):
        return self.vec

    def set_vec(self, vec):
        self.vec = vec

    def get_thro(self):
        return self.thro

    def set_thro(self, thro):
        self.thro = thro
        self.uhd_usrp_source_0.set_sample_rate(self.thro)

    def get_low(self):
        return self.low

    def set_low(self, low):
        self.low = low

    def get_hydro(self):
        return self.hydro

    def set_hydro(self, hydro):
        self.hydro = hydro
        self.qtgui_sink_x_0.set_frequency_range(self.hydro, 0)
        self.uhd_usrp_source_0.set_center_freq(self.hydro, 0)

    def get_high(self):
        return self.high

    def set_high(self, high):
        self.high = high
