
import random
import re
from aqt import QButtonGroup, QCheckBox, QColor, QColorDialog, QDialog, QDoubleSpinBox, QFrame, QHBoxLayout, QIcon, QLineEdit, QRadioButton, QSize, QStyle, QTabWidget, QTextBrowser, QWidget,Qt
from aqt import QVBoxLayout, QLabel, QPushButton
from aqt import mw
from aqt.utils import tooltip
from aqt.utils import tr
from os.path import join, dirname
from aqt import QPixmap,gui_hooks
from aqt.utils import openLink
from .shige_addons import add_shige_addons_tab

WIDGET_HEIGHT = 550

DEBUG_MODE = True

IS_RATE_THIS = "is_rate_this"
CHANGE_LOG_DAY = "is_change_log_2024_04_05"

THE_ADDON_NAME = "Progress bar (Fork by Shige)"
SHORT_ADDON_NAME = "Progress bar"

BANNER_WIDTH = 450

SET_LINE_EDID_WIDTH = 400
MAX_LABEL_WIDTH = 100
ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
RATE_THIS = None
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    RATE_THIS = True

RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"
POPUP_PNG = "popup_shige.png"

#🔴使ってない
NEW_FEATURE = """
-[ Progress Bar Settings Window ]
    It can be opened from Tools.
-[ Change Calculation Method ]
    [1] Each deck : Default, Reset after reboot.
    [2] All decks : Beta, Not reset after reboot.
-[ Quick Settings ]
    Right-click on progress bar to open settings.
"""

RATE_THIS_TEXT = """
[ Update : {addon} ]

Shigeyuki :
Hello, thank you for using this add-on!
I developed new options!
{new_feature}

Feel free to contact me with any problems or requests.
Thank you!

""".format(addon=SHORT_ADDON_NAME, new_feature=NEW_FEATURE)


class Shige_Addon_Config(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.changes_detected = False

        config = mw.addonManager.getConfig(__name__)

        self.showPercent = config["showPercent"] # false
        self.showNumber = config["showNumber"] # false
        self.textColor = config["textColor"] # "aliceblue"
        self.backgroundColor = config["backgroundColor"] # "rgba(0, 0, 0, 0)"
        self.foregroundColor = config["foregroundColor"] # "#3399cc"
        self.borderRadius = config["borderRadius"] # 0
        value = re.sub(r'\D', '', config["maxWidth"])
        self.maxWidth = min(max(0, int(value)), 50) # "20"
        # self.maxWidth = int(config["maxWidth"]) # "20"
        # self.maxWidth = int(config["maxWidth"].replace('px', '')) if 'px' in config["maxWidth"] else int(config["maxWidth"])
        self.font_size = config.get("fontSize", "20px") 
        self.progressbarType = config["progressbarType"] # "type_A"
        self.includeNew = config["includeNew"]
        self.hide_Progressbar = config.get("hide_Progressbar", False)
        self.show_progress_bar_on_bottom = config.get("show_progress_bar_on_bottom", False)


        self.use_gradation = config.get("use_gradation", True)
        self.chunk_color_left = config.get("chunk_color_left", "#3399cc")
        self.chunk_color_center = config.get("chunk_color_center", "#4cedff")
        self.chunk_color_right = config.get("chunk_color_right", "#3399cc")

        self.show_left_time =  config.get("show_left_time", True)


        addon_path = dirname(__file__)
        self.setWindowIcon(QIcon(join(addon_path, r"icon.png")))

        # Set image on QLabel
        self.patreon_label = QLabel()
        patreon_banner_path = join(addon_path, r"banner.jpg")
        pixmap = QPixmap(patreon_banner_path)
        pixmap = pixmap.scaledToWidth(BANNER_WIDTH, Qt.TransformationMode.SmoothTransformation)
        self.patreon_label.setPixmap(pixmap)
        self.patreon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.patreon_label.setFixedSize(pixmap.width(), pixmap.height())
        self.patreon_label.mousePressEvent = self.open_patreon_Link
        self.patreon_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.patreon_label.enterEvent = self.patreon_label_enterEvent
        self.patreon_label.leaveEvent = self.patreon_label_leaveEvent

        self.setWindowTitle(THE_ADDON_NAME)

        button = QPushButton('OK')
        button.clicked.connect(self.handle_button_clicked)
        # button.clicked.connect(self.hide)
        button.setFixedWidth(120)

        button2 = QPushButton('Cancel')
        button2.clicked.connect(self.cancelSelect)
        button2.clicked.connect(self.hide)
        button2.setFixedWidth(120)


        from ..shige_pop.button_manager import mini_button
        if RATE_THIS:
            button3 = QPushButton('👍️RateThis')
            button3.clicked.connect(self.open_rate_this_Link)
            mini_button(button3)
            button3.setFocusPolicy(Qt.FocusPolicy.NoFocus)


        button4 = QPushButton('💖Patreon')
        button4.clicked.connect(self.open_patreon_Link)
        mini_button(button4)
        button4.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        report_button = QPushButton("🚨Report")
        report_button.clicked.connect(lambda: openLink("https://shigeyukey.github.io/shige-addons-wiki/progress-bar.html#report"))
        report_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        mini_button(report_button)






        # ｳｨﾝﾄﾞｳにQFontComboBoxとQLabelとQPushButtonを追加
        layout = QVBoxLayout()


        #-----------------------------
        # self.overview_zoom_label,self.overview_zoom_spinbox = self.create_spinbox(
        # "[ overview zoom ]", 0.1, 5, self.overview_zoom, 70, 1, 0.1,"overview_zoom")

        layout.addWidget(self.create_separator())#-------------
        home_change_label = QLabel("These settings can be quickly changed.")
        home_change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(home_change_label)
        layout.addWidget(self.create_separator())#-------------



        self.borderRadius # 0
        self.borderRadius_label,self.borderRadius_spinbox  = self.create_spinbox(
        "[ Border Radius ] 0 - 9", 0, 9, self.borderRadius, 70, 0, 1,"borderRadius"
        )

        self.maxWidth # "20"
        self.maxWidth_label,self.maxWidth_spinbox  = self.create_spinbox(
        "[ Bar Height ] 0 - 50, Default : 20", 0, 50, self.maxWidth, 70, 0, 1,"maxWidth"
        )
        self.font_size_label, self.font_size_spinbox = self.create_spinbox(
        "[ Font Size ] 8 - 25, Default : 20", 8, 20, int(self.font_size.replace('px', '')), 70, 0, 1, "fontSize"
        )


        # new option ------------
        # if config[IF_RATE_DHIS]:
        #     self.manually_force_zoom_label = self.create_checkbox(
        #         "manually force zoom",  "manually_force_zoom")
        #     self.add_icon_to_checkbox(self.manually_force_zoom_label, "Do not automatically set the zoom value.")
        #-------------------------

        self.showPercent
        self.showPercent_label = self.create_checkbox( "Show Percent", "showPercent")
        self.showNumber
        self.showNumber_label = self.create_checkbox( "Show Number", "showNumber")
        self.includeNew
        self.includeNew_label =  self.create_checkbox( "Include New Cards", "includeNew")
        self.hide_Progressbar
        self.hide_Progressbar_label =  self.create_checkbox("Hide Progressbar", "hide_Progressbar")
        self.show_progress_bar_on_bottom
        self.show_progress_bar_on_bottom_label =  self.create_checkbox("Show progress bar on bottom","show_progress_bar_on_bottom")

        self.show_left_time
        self.show_left_time_lable = self.create_checkbox("show time left","show_left_time")



        # layout.addWidget(self.patreon_label)

        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.showPercent_label)
        stats_layout.addWidget(self.showNumber_label)
        stats_layout.addWidget(self.show_left_time_lable)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        layout.addWidget(self.create_separator())#-------------

        color_tab_label = QLabel("[ Bar Color ] AlphaChannel is transparency.")
        color_tab_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(color_tab_label)

        self.textColor
        self.color_button = QPushButton()
        self.color_button.setFixedWidth(70)
        self.color_button.clicked.connect(self.choose_text_color)
        if self.textColor is not None:
            self.color_button.setStyleSheet(f"background-color: {self.textColor}")
        color_label = QLabel("Text Color (Default : #f0f8ff)")
        color_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.color_button)
        h_layout.addWidget(color_label)
        layout.addLayout(h_layout)


        self.backgroundColor
        self.color_button_2 = QPushButton()
        self.color_button_2.setFixedWidth(70)
        self.color_button_2.clicked.connect(self.choose_color)
        if self.backgroundColor is not None:
            self.color_button_2.setStyleSheet(f"background-color: {self.backgroundColor}")
        backgroundColor_label = QLabel("Background Color (Default : AlphaChannel 0)")
        backgroundColor_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        h2_layout = QHBoxLayout()
        h2_layout.addWidget(self.color_button_2)
        h2_layout.addWidget(backgroundColor_label)
        layout.addLayout(h2_layout)

        self.foregroundColor
        self.color_button_3 = QPushButton()
        self.color_button_3.setFixedWidth(70)
        self.color_button_3.clicked.connect(self.choose_foreground_color)
        if self.foregroundColor is not None:
            self.color_button_3.setStyleSheet(f"background-color: {self.foregroundColor}")
        foregroundColor_label = QLabel("Foreground Color (Default : #3399cc)")
        foregroundColor_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        h3_layout = QHBoxLayout()
        h3_layout.addWidget(self.color_button_3)
        h3_layout.addWidget(foregroundColor_label)
        layout.addLayout(h3_layout)

        layout.addWidget(self.create_separator())#-------------


        gra_layout = QHBoxLayout()
        gradation_label = QLabel("[ Gradient ]")
        gradation_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        gra_layout.addWidget(gradation_label)

        self.use_gradation
        self.use_gradation_label = self.create_checkbox( "Use Gradient", "use_gradation")
        gra_layout.addWidget(self.use_gradation_label)

        gra_layout.addStretch()
        layout.addLayout(gra_layout)

        self.chunk_color_right
        self.create_color_button("chunk_color_left", "Left Color", layout)
        self.chunk_color_center
        self.create_color_button("chunk_color_center", "Cneter Color", layout)
        self.chunk_color_left
        self.create_color_button("chunk_color_right", "Right Color", layout)



        # 🟢
        layout02 = QVBoxLayout()
        layout02.addWidget(self.create_separator())#-------------
        home_change_label_02 = QLabel("These settings can be quickly changed.")
        home_change_label_02.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout02.addWidget(home_change_label_02)
        layout02.addWidget(self.create_separator())#-------------


        layout02.addWidget(self.borderRadius_label)
        self.add_widget_with_spacing(layout02, self.borderRadius_spinbox)

        layout02.addWidget(self.maxWidth_label)
        self.add_widget_with_spacing(layout02, self.maxWidth_spinbox)
        layout02.addWidget(self.font_size_label)
        self.add_widget_with_spacing(layout02, self.font_size_spinbox)

        layout02.addWidget(self.hide_Progressbar_label)
        layout02.addWidget(self.show_progress_bar_on_bottom_label)

        # ------ ﾗｼﾞｵﾎﾞﾀﾝB ----------------------
        # 🟢
        layout03 = QVBoxLayout()
        layout03.addWidget(self.create_separator())#-------------
        need_restart_label = QLabel("These settings require a restart of Anki.")
        need_restart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout03.addWidget(need_restart_label)
        layout03.addWidget(self.create_separator())#-------------


        layout03.addWidget(QLabel("[ Calculation Method ]"))
        button_dict = {"Each deck (Restarting Anki will reset the card counts)": "type_A",
                            "All decks (Beta : Card counts are not reset after restarting Anki)": "type_B"
                            }
        self.progressbarType
        radio_attr = "progressbarType"
        layout03.addLayout(self.create_radio_buttons(button_dict, radio_attr))
        # --------------------------------------------

        layout03.addWidget(self.create_separator())#-------------
        layout03.addWidget(self.includeNew_label)
        # layout.addWidget(self.create_separator())#-------------
        # text_01 = QLabel("- Right click on progress bar to open settings.")
        # text_01.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # layout.addWidget(text_01)
        # text_02 = QLabel("- Settings will take effect after restarting Anki.")
        # text_02.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # layout.addWidget(text_02)

        # layout.addWidget(self.review_zoom_label)
        # self.add_widget_with_spacing(layout,self.review_zoom_spinbox)

        # layout.addLayout(self.zoom_in_shortcut_label)
        # layout.addLayout(self.zoom_out_shortcut_label)
        # layout.addLayout(self.reset_shortcut_label)

        # new option ------------
        # if config[IF_RATE_DHIS]:
        #     layout.addWidget(self.create_separator())#-------------
            # layout.addWidget(self.manually_force_zoom_label)
        # ----------------------

        tab_widget = QTabWidget(self)

        tab_theme = QWidget()
        layout.addStretch(1)
        tab_theme.setLayout(layout)

        tab_option_02 = QWidget()
        layout02.addStretch(1)
        tab_option_02.setLayout(layout02)

        tab_option_03 = QWidget()
        layout03.addStretch(1)
        tab_option_03.setLayout(layout03)

        # --------------------------

        tab_moreInfo = QWidget()

        moreInfo_layout = QVBoxLayout()
        from .more_info import more_info_text
        text_edit = QTextBrowser()
        text_edit.setReadOnly(True)
        text_edit.setOpenExternalLinks(True)
        more_info = more_info_text(THE_ADDON_NAME, ADDON_PACKAGE)
        text_edit.setHtml("<html><body>" + more_info + "</body></html>")

        addon_path = dirname(__file__)
        icon = QPixmap(join(addon_path,POPUP_PNG))
        icon_label = QLabel()
        icon_label.setPixmap(icon)

        hbox = QHBoxLayout()
        hbox.addWidget(icon_label)
        hbox.addWidget(text_edit)
        moreInfo_layout.addLayout(hbox)

        # moreInfo_layout.addStretch(1)
        tab_moreInfo.setLayout(moreInfo_layout)


        # --------------------------


        tab_widget.addTab(tab_theme,"Option1")
        tab_widget.addTab(tab_option_02,"Option2")
        tab_widget.addTab(tab_option_03,"Option3")
        tab_widget.addTab(tab_moreInfo, "MoreInfo")
        add_shige_addons_tab(self, tab_widget)


        # --------------------------


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.patreon_label)
        main_layout.addWidget(tab_widget)

        button_layout = QHBoxLayout()

        button_layout.addStretch(1)

        button_layout.addWidget(button)
        button_layout.addWidget(button2)
        if RATE_THIS:button_layout.addWidget(button3)
        button_layout.addWidget(button4)
        button_layout.addWidget(report_button)


        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


        self.adjust_self_size()


    def adjust_self_size(self):
        min_size = self.layout().minimumSize()
        # self.resize(min_size.width(), min_size.height())
        self.resize(min_size.width(), WIDGET_HEIGHT)



    def create_color_button(self, color_attr, label_text, layout:QHBoxLayout):
        color_button = QPushButton()
        color_button.setFixedWidth(70)

        def choose_colors():
            get_color = self.get_color(getattr(self, color_attr))
            if get_color is not None:
                setattr(self, color_attr, get_color)
                color_button.setStyleSheet(f"background-color: {get_color}")
        color_button.clicked.connect(choose_colors)

        color = getattr(self, color_attr)
        if color is not None:
            color_button.setStyleSheet(f"background-color: {color}")
        color_label = QLabel(label_text)
        color_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        h_layout = QHBoxLayout()
        h_layout.addWidget(color_button)
        h_layout.addWidget(color_label)
        layout.addLayout(h_layout)




    # ﾗｼﾞｵﾎﾞﾀﾝを作成する関数===============
    def create_radio_buttons(self, button_dict, radio_attr):
        layout = QVBoxLayout()
        button_group = QButtonGroup(layout)
        for button_name, button_value in button_dict.items():
            radio_button = QRadioButton(button_name)
            radio_button.setChecked(getattr(self, radio_attr) == button_value)
            radio_button.toggled.connect(
                lambda checked,
                button_value=button_value: self.update_radio_buttons(checked, button_value, radio_attr))
            # layout.addWidget(radio_button)
            self.add_widget_with_spacing(layout, radio_button)
            button_group.addButton(radio_button)
        return layout

    def update_radio_buttons(self, checked, button_value, radio_attr):
        if checked:
            setattr(self, radio_attr, button_value)
    #============================================





    #------ 色を取得する関数(透明度あり) ----
    def choose_text_color(self):
        color = self.get_color(self.textColor)
        if color is not None:
            self.textColor = color
            self.color_button.setStyleSheet(f"background-color: {self.textColor}")

    def choose_color(self):
        color = self.get_color(self.backgroundColor)
        if color is not None:
            self.backgroundColor = color
            self.color_button_2.setStyleSheet(f"background-color: {self.backgroundColor}")

    def choose_foreground_color(self):
        color = self.get_color(self.foregroundColor)
        if color is not None:
            self.foregroundColor = color
            self.color_button_3.setStyleSheet(f"background-color: {self.foregroundColor}")


    def get_color(self, current_color=None):
        dialog = QColorDialog()
        dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, on=True)
        if current_color == "rgba(0, 0, 0, 0)":
            current_color = "#00000000"
        if current_color is not None:
            dialog.setCurrentColor(QColor(current_color))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            color = dialog.selectedColor()
            if color.isValid():
                return color.name(QColor.NameFormat.HexArgb)
            return None
    #----------------------------





    # ﾁｪｯｸﾎﾞｯｸｽを生成する関数=======================
    def create_checkbox(self, label, attribute_name):
        checkbox = QCheckBox(label, self)
        checkbox.setChecked(getattr(self, attribute_name))

        def handler(state):
            if state == 2:
                setattr(self, attribute_name, True)
            else:
                setattr(self, attribute_name, False)

        checkbox.stateChanged.connect(handler)
        return checkbox

    # ﾁｪｯｸﾎﾞｯｸｽにﾂｰﾙﾁｯﾌﾟとﾊﾃﾅｱｲｺﾝを追加する関数=========
    def add_icon_to_checkbox(self, checkbox: QCheckBox, tooltip_text):
        qtip_style = """
            QToolTip {
                border: 1px solid black;
                padding: 5px;
                font-size: 2em;
                background-color: #303030;
                color: white;
            }
        """
        checkbox.setStyleSheet(qtip_style)
        checkbox.setToolTip(tooltip_text)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        checkbox_height = checkbox.height()
        checkbox.setIcon(QIcon(icon.pixmap(checkbox_height, checkbox_height)))
    #=================================================


    # ｾﾊﾟﾚｰﾀを作成する関数=========================
    def create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("border: 1px solid gray")
        return separator
    # =================================================


    # ﾚｲｱｳﾄにｽﾍﾟｰｽを追加する関数=======================
    def add_widget_with_spacing(self,layout, widget):
        hbox = QHBoxLayout()
        hbox.addSpacing(15)  # ｽﾍﾟｰｼﾝｸﾞを追加
        hbox.addWidget(widget)
        hbox.addStretch(1)
        layout.addLayout(hbox)

    # ------------ patreon label----------------------
    def patreon_label_enterEvent(self, event):
        addon_path = dirname(__file__)
        patreon_banner_hover_path = join(addon_path, r"Patreon_banner.jpg")
        self.pixmap = QPixmap(patreon_banner_hover_path)
        self.pixmap = self.pixmap.scaledToWidth(BANNER_WIDTH, Qt.TransformationMode.SmoothTransformation)
        self.patreon_label.setPixmap(self.pixmap)

    def patreon_label_leaveEvent(self, event):
        addon_path = dirname(__file__)
        patreon_banner_hover_path = join(addon_path, r"banner.jpg")
        self.pixmap = QPixmap(patreon_banner_hover_path)
        self.pixmap = self.pixmap.scaledToWidth(BANNER_WIDTH, Qt.TransformationMode.SmoothTransformation)
        self.patreon_label.setPixmap(self.pixmap)
    # ------------ patreon label----------------------

    #-- open patreon link-----
    def open_patreon_Link(self,url):
        openLink("http://patreon.com/Shigeyuki")

    #-- open rate this link-----
    def open_rate_this_Link(self,url):
        openLink(RATE_THIS_URL)
        toggle_rate_this()

    # --- cancel -------------
    def cancelSelect(self):
        emoticons = [":-/", ":-O", ":-|"]
        selected_emoticon = random.choice(emoticons)
        tooltip("Canceled " + selected_emoticon)
        self.close()
    #-----------------------------


    #----------------------------
    # ｽﾋﾟﾝﾎﾞｯｸｽを作成する関数=========================
    def create_spinbox(self, label_text, min_value,
                                max_value, initial_value, width,
                                decimals, step, attribute_name):
        def spinbox_handler(value):
            value = round(value, 1)
            if decimals == 0:
                setattr(self, attribute_name, f"{int(value)}px")
            else:
                setattr(self, attribute_name, value)

        label = QLabel(label_text, self)
        spinbox = QDoubleSpinBox(self)
        spinbox.setMinimum(min_value)
        spinbox.setMaximum(max_value)
        spinbox.setValue(initial_value)
        spinbox.setFixedWidth(width)
        spinbox.setDecimals(decimals)
        spinbox.setSingleStep(step)
        spinbox.valueChanged.connect(spinbox_handler)
        return label, spinbox
    #=================================================


    # ﾃｷｽﾄﾎﾞｯｸｽを作成する関数=========================
    def create_line_edits_and_labels(self, list_attr_name, list_items, b_name, b_index=None):
        main_layout = QVBoxLayout()
        items = list_items if isinstance(list_items, list) else [list_items]
        for i, item in enumerate(items):
            line_edit = QLineEdit(item)
            line_edit.textChanged.connect(lambda text,
                                        i=i,
                                        name=list_attr_name: self.update_list_item(name, i, text))
            line_edit.setMaximumWidth(SET_LINE_EDID_WIDTH)

            if i == 0:
                layout = QHBoxLayout()
                if b_index is not None:
                    b_name_attr = getattr(self, b_name)
                    label_edit = QLineEdit(b_name_attr[b_index])
                    label_edit.textChanged.connect(lambda text,
                                                i=i,
                                                b_name=b_name: self.update_label_item(b_name, b_index, text))
                    label_edit.setFixedWidth(MAX_LABEL_WIDTH)
                    layout.addWidget(label_edit)
                else:
                    label = QLabel(b_name)
                    label.setFixedWidth(MAX_LABEL_WIDTH)
                    layout.addWidget(label)
            else:
                label = QLabel()
                label.setFixedWidth(MAX_LABEL_WIDTH)
                layout = QHBoxLayout()
                layout.addWidget(label)

            line_edit = QLineEdit(item)
            line_edit.textChanged.connect(lambda text,
                                        i=i,
                                        name=list_attr_name: self.update_list_item(name, i, text))
            line_edit.setMaximumWidth(SET_LINE_EDID_WIDTH)
            layout.addWidget(line_edit)
            main_layout.addLayout(layout)
        return main_layout

    def update_label_item(self, b_name, index, text):
        update_label = getattr(self,b_name)
        update_label[index] = text
    def update_list_item(self, list_attr_name, index, text):
        # list_to_update = getattr(self, list_attr_name)
        # list_to_update[index] = text
        list_to_update = getattr(self, list_attr_name)
        if isinstance(list_to_update, list):
            list_to_update[index] = text
        else:
            setattr(self, list_attr_name, text)
    # ===================================================

    def handle_button_clicked(self):
        self.save_config_fontfamiles()
        from ..shige_progress_bar import after_change_shige_settings
        after_change_shige_settings(mw.state)
        if self.changes_detected:
            check_restart_anki()

        emoticons = [":-)", ":-D", ";-)"]
        selected_emoticon = random.choice(emoticons)
        tooltip("Changed setting " + selected_emoticon)
        self.close()



    def save_config_fontfamiles(self):
        config = mw.addonManager.getConfig(__name__)

        config["showPercent"] = self.showPercent
        config["showNumber"] = self.showNumber
        config["textColor"] = self.textColor
        config["backgroundColor"] = self.backgroundColor
        config["foregroundColor"] = self.foregroundColor
        config["borderRadius"] = self.borderRadius
        config["maxWidth"] = str(self.maxWidth)
        config["fontSize"] = self.font_size

        if (config.get("progressbarType", "type_A") != self.progressbarType
            or config.get("includeNew", True) != self.includeNew):
            self.changes_detected = True

        config["progressbarType"] = self.progressbarType
        config["includeNew"] = self.includeNew
        config["hide_Progressbar"] = self.hide_Progressbar

        config["show_progress_bar_on_bottom"] = self.show_progress_bar_on_bottom

        config["use_gradation"] = self.use_gradation
        config["chunk_color_left"] = self.chunk_color_left
        config["chunk_color_center"] = self.chunk_color_center
        config["chunk_color_right"] = self.chunk_color_right

        config["show_left_time"] = self.show_left_time

        from ..shige_progress_bar import need_update_config
        need_update_config()

        mw.addonManager.writeConfig(__name__, config)

        # --------------show message box-----------------
        # try:some_restart_anki =tr.preferences_some_settings_will_take_effect_after()
        # except:some_restart_anki ="Some settings will take effect after you restart Anki."
        # tooltip(some_restart_anki)
        # --------------show message box-----------------


def setProgressbarConfig():
    my_config = Shige_Addon_Config(mw)
    my_config.show()

def open_config_modal():
    my_config = Shige_Addon_Config(mw)
    if hasattr(my_config, 'exec'):
        my_config.exec()
    elif hasattr(my_config, 'exec_'):
        my_config.exec_()
    else:
        my_config.show()



    # config = mw.addonManager.getConfig(__name__)
    # if (config[IS_RATE_THIS]):
    #     font_viewer = Shige_Addon_Config(mw)
    #     font_viewer.show()
    # else:
    #     change_log_popup_B()


# ------- Rate This PopUp ---------------

def set_gui_hook_rate_this():
    gui_hooks.main_window_did_init.append(change_log_popup)

def change_log_popup(*args,**kwargs):
    try:
        config = mw.addonManager.getConfig(__name__)
        if (config[IS_RATE_THIS] == False
            and config[CHANGE_LOG_DAY] == False
            ):

            dialog = CustomDialog()
            if hasattr(dialog, 'exec'):result = dialog.exec() # Qt6
            else:result = dialog.exec_() # Qt5

            if result == QDialog.DialogCode.Accepted:
                open_rate_this_Link(RATE_THIS_URL)
                toggle_rate_this()
            elif  result == QDialog.DialogCode.Rejected:
                toggle_changelog()

    except Exception as e:
        if DEBUG_MODE:raise e
        else:pass


def change_log_popup_B(*args,**kwargs):
    try:
        config = mw.addonManager.getConfig(__name__)
        if (config[IS_RATE_THIS] == False):

            dialog = CustomDialog()
            if hasattr(dialog, 'exec'):result = dialog.exec() # Qt6
            else:result = dialog.exec_() # Qt5

            if result == QDialog.DialogCode.Accepted:
                open_rate_this_Link(RATE_THIS_URL)
                toggle_rate_this()
            elif  result == QDialog.DialogCode.Rejected:
                toggle_changelog()

    except Exception as e:
        print(e)
        pass


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        addon_path = dirname(__file__)
        icon = QPixmap(join(addon_path,POPUP_PNG))
        layout = QVBoxLayout()

        self.setWindowTitle(THE_ADDON_NAME)

        icon_label = QLabel()
        icon_label.setPixmap(icon)

        hbox = QHBoxLayout()

        rate_this_label = QLabel(RATE_THIS_TEXT)
        rate_this_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hbox.addWidget(icon_label)
        hbox.addWidget(rate_this_label)

        layout.addLayout(hbox)

        button_layout = QHBoxLayout()

        self.yes_button = QPushButton("Activate (RateThis)")
        self.yes_button.clicked.connect(self.accept)
        self.yes_button.setFixedWidth(200)
        button_layout.addWidget(self.yes_button)

        self.no_button = QPushButton("No")
        self.no_button.clicked.connect(self.reject)
        self.no_button.setFixedWidth(100)
        button_layout.addWidget(self.no_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

def open_rate_this_Link(url):
    openLink(url)

def toggle_rate_this():
    config = mw.addonManager.getConfig(__name__)
    config[IS_RATE_THIS] = True
    config[CHANGE_LOG_DAY] = True
    mw.addonManager.writeConfig(__name__, config)

def toggle_changelog():
    config = mw.addonManager.getConfig(__name__)
    config[CHANGE_LOG_DAY] = True
    mw.addonManager.writeConfig(__name__, config)

# -----------------------------------
def check_restart_anki():
    menu = mw.form.menuTools
    for action in menu.actions():
        if action.text() == "Anki Restart":
            submenu = action.menu()
            for subaction in submenu.actions():
                if subaction.text() == "Restart Anki now":
                    restart_button = QPushButton("Restart")
                    restart_button.clicked.connect(subaction.trigger)
                    create_anki_restart_dialog(restart_button)

def create_anki_restart_dialog(restart_button:QPushButton):
    dialog = QDialog()
    dialog.setModal(True)
    layout = QVBoxLayout()

    Addon_path = dirname(__file__)
    Icon_path = join(Addon_path, r"Restart.png")
    shige_icon_path = join(Addon_path, r"icon.png")
    dialog.setWindowIcon(QIcon(shige_icon_path))

    # text_label = QLabel("Restart Anki now using AnkiRestart?")

    layout = QVBoxLayout()
    hbox = QHBoxLayout()
    label = QLabel()
    pixmap = QPixmap(Icon_path)
    pixmap = pixmap.scaledToHeight(35)
    label.setPixmap(pixmap)
    label.setFixedSize(pixmap.size())
    hbox.addWidget(label)

    text = QLabel("Restart Anki now?")
    hbox.addWidget(text)
    layout.addLayout(hbox)

    dialog.setWindowTitle("AnkiRestart by Shige")
    # layout.addWidget(text_label)
    restart_button.setFixedWidth(100)
    no_button = QPushButton("No")
    no_button.setFixedWidth(100)
    no_button.clicked.connect(dialog.close)
    button_layout = QHBoxLayout()
    button_layout.addWidget(restart_button)
    button_layout.addWidget(no_button)
    layout.addLayout(button_layout)
    dialog.setLayout(layout)
    try:dialog.exec()
    except:dialog.exec_()

