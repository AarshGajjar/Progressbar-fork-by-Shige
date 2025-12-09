# Anki Add-on: Progress Bar
# Copyright:
#             (c) Unknown author (nest0r/Ja-Dark?) 2017
#             (c) SebastienGllmt 2017 <https://github.com/SebastienGllmt/>
#             (c) Glutanimate 2017-2018 <https://glutanimate.com/>
#             (c) liuzikai 2018-2020 <https://github.com/liuzikai>
#             (c) BluMist 2022 <https://github.com/BluMist>
#             (c) Unknown author 2023
#             (c) Shigeyuki 2024 <https://www.patreon.com/Shigeyuki>

# Shows progress in the Reviewer in terms of passed cards per session.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.



from typing import Optional
from aqt import QColor, QDockWidget, QPalette, QProgressBar, QStyleFactory, QWidget, Qt, mw, gui_hooks
from aqt import QTimer
from time import time
from datetime import datetime

__version__ = '2.0.1'

class CustomProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.perform_action1()
        super().mousePressEvent(event)


    # def contextMenuEvent(self, event):
    #     contextMenu = QMenu(self)

    #     action1 = QAction("⚙Open Settings", self)
    #     action1.triggered.connect(self.perform_action1)
    #     contextMenu.addAction(action1)

    #     try:contextMenu.exec(QCursor.pos()) #pyQt6
    #     except:contextMenu.exec_(QCursor.pos()) #pyQt5

    def perform_action1(self):
        from .shige_config.progressbar_config import setProgressbarConfig
        setProgressbarConfig()

QProgressBar = CustomProgressBar
session_start_time = None  # Initialize session start time
cards_done_in_session = 0  # Initialize cards done in the current session
### USER CONFIG ###

def getConfig(arg, default=""):
    config = mw.addonManager.getConfig(__name__)
    if config:
        return config.get(arg, default)
    else:
        return default

def getConfigDockArea():
    config = mw.addonManager.getConfig(__name__)
    if config and config.get("show_progress_bar_on_bottom", False):
        return Qt.DockWidgetArea.BottomDockWidgetArea
    return Qt.DockWidgetArea.TopDockWidgetArea

# ｶｰﾄﾞの種類
includeNew = getConfig("includeNew", True)
includeRev = True
includeLrn = True

# ｶｰﾄﾞの種類
# includeNew = True
# includeRev = True
# includeLrn = True

# ﾚﾋﾞｭｰが尽きたらnewｶｰﾄﾞを含める
includeNewAfterRevs = True

# 重み計算
newWeight = 2
revWeight = 1
lrnWeight = 1

# 後ろに戻さない
forceForward = False

### PROGRESS BAR ###


TYPE_A = "type_A"
TYPE_B = "type_B"
PB_TYPE  = getConfig("progressbarType", "type_A")

showPercent = getConfig("showPercent", False)
showNumber = getConfig("showNumber", False)

qtxt = getConfig("textColor", "aliceblue")
qbg = getConfig("backgroundColor", "rgba(0, 0, 0, 0)")
qfg = getConfig("foregroundColor", "#3399cc")
qbr = getConfig("borderRadius", 0)

maxWidth = getConfig("maxWidth", "5px")
font_size = getConfig("fontSize", "20px") 

scrollingBarWhenEditing = True

orientationHV = Qt.Orientation.Horizontal

invertTF = False # 右から左
session_timer = None




# dockArea = Qt.DockWidgetArea.TopDockWidgetArea
# dockArea = Qt.DockWidgetArea.BottomDockWidgetArea
# dockArea = getConfigDockArea()

pbStyle = ""
'''pbStyle options (insert a quoted word above):
    -- "plastique", "windowsxp", "windows", "windowsvista", "motif", "cde", "cleanlooks"
    -- "macintosh", "gtk", or "fusion" might also work
    -- "windowsvista" unfortunately ignores custom colors, due to animation?
    -- Some styles don't reset bar appearance fully on undo. An annoyance.
    -- Themes gallery: http://doc.qt.io/qt-4.8/gallery.html'''


change_config = False
def need_update_config():
    global change_config
    change_config = True

def didConfigChange():
    didChange = False

    global showPercent
    global showNumber

    global qtxt
    global qbg
    global qfg
    global qbr

    global maxWidth

    global change_config
    if change_config:
        didChange = True
        change_config = False


    if showPercent != getConfig("showPercent", False):
        showPercent = getConfig("showPercent", False)
        didChange = True

    if showNumber != getConfig("showNumber", False):
        showNumber = getConfig("showNumber", False)
        didChange = True

    if qtxt != getConfig("textColor", "aliceblue"):
        qtxt = getConfig("textColor", "aliceblue")
        didChange = True

    if qbg != getConfig("backgroundColor", "rgba(0, 0, 0, 0)"):
        qbg = getConfig("backgroundColor", "rgba(0, 0, 0, 0)")
        didChange = True

    if qfg != getConfig("foregroundColor", "#3399cc"):
        qfg = getConfig("foregroundColor", "#3399cc")
        didChange = True

    if qbr != getConfig("borderRadius", 0):
        qbr = getConfig("borderRadius", 0)
        didChange = True

    if maxWidth != getConfig("maxWidth", "5px"):
        maxWidth = getConfig("maxWidth", "5px")
        didChange = True

    if didChange:
        global palette
        global orientationHV
        global restrictSize

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, QColor(qbg))
        palette.setColor(QPalette.ColorRole.Base, QColor(qfg))
        palette.setColor(QPalette.ColorRole.Base, QColor(qbg))
        palette.setColor(QPalette.ColorRole.Base, QColor(qtxt))
        palette.setColor(QPalette.ColorRole.Base, QColor(qbg))

        if maxWidth:
            if orientationHV == Qt.Orientation.Horizontal:
                # restrictSize = "max-height: %s;" % maxWidth
                restrictSize = "height: %s; max-height: %s;" % (maxWidth, maxWidth)
            else:
                # restrictSize = "max-width: %s;" % maxWidth
                restrictSize = "width: %s; max-width: %s;" % (maxWidth, maxWidth)
        else:
            restrictSize = ""

    return didChange

###  USER CONFIGURATION END  ###

remainCount = {}
doneCount  = {}
totalCount = {}

currDID: Optional[int] = None

nmStyleApplied = 0
nmUnavailable = 1
progressBar_2: Optional[QProgressBar] = None

pbdStyle = QStyleFactory.create("%s" % pbStyle)

palette = QPalette()
palette.setColor(QPalette.ColorRole.Base, QColor(qbg))
palette.setColor(QPalette.ColorRole.Highlight, QColor(qfg))
palette.setColor(QPalette.ColorRole.Button, QColor(qbg))
palette.setColor(QPalette.ColorRole.WindowText, QColor(qtxt))
palette.setColor(QPalette.ColorRole.Window, QColor(qbg))

if maxWidth:
    if orientationHV == Qt.Orientation.Horizontal:
        # restrictSize = "max-height: %s;" % maxWidth
        restrictSize = "height: %s; max-height: %s;" % (maxWidth, maxWidth)
    else:
        # restrictSize = "max-width: %s;" % maxWidth
        restrictSize = "Width: %s; max-Width: %s;" % (maxWidth, maxWidth)
else:
    restrictSize = ""

def initPB() -> None:
    global progressBar_2
    if not progressBar_2:
        progressBar_2 = QProgressBar()
        _dock(progressBar_2)
    progressBar_2.setTextVisible(showPercent or showNumber)
    progressBar_2.setInvertedAppearance(invertTF)
    progressBar_2.setOrientation(orientationHV)
    if pbdStyle is None:
        use_gradation = getConfig("use_gradation", True)
        font_size = getConfig("fontSize", "20px")
        if not use_gradation:
            progressBar_2.setStyleSheet(
                '''
                    QProgressBar
                    {
                        text-align:center;
                        color:%s;
                        background-color: %s;
                        border-radius: %dpx;
                        font-size: %s;
                        %s
                    }
                    QProgressBar::chunk
                    {
                        background-color: %s;
                        margin: 0px;
                        border-radius: %dpx;
                    }
                    ''' % (qtxt, qbg, qbr, font_size, restrictSize, qfg, qbr))

        else:
            qfg_left = getConfig("chunk_color_left", "#3399cc")
            qfg_center = getConfig("chunk_color_center", "#4cedff")
            qfg_right = getConfig("chunk_color_right", "#3399cc")

            progressBar_2.setStyleSheet(
                '''
                    QProgressBar
                    {
                        text-align:center;
                        color:%s;
                        background-color: %s;
                        border-radius: %dpx;
                        font-size: %s;
                        %s
                    }
                    QProgressBar::chunk
                    {
                        background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 %s, stop: 0.5 %s, stop: 1 %s);
                        margin: 0px;
                        border-radius: %dpx;
                    }
                    ''' % (qtxt, qbg, qbr, font_size, restrictSize, qfg_left, qfg_center, qfg_right, qbr))

    else:
        progressBar_2.setStyle(pbdStyle)
        progressBar_2.setPalette(palette)

dockWidgetPB = None

def _dock(pb: QProgressBar) -> QDockWidget:
    global dockWidgetPB
    dockWidgetPB = QDockWidget()
    tWidget = QWidget()
    dockWidgetPB.setWidget(pb)
    dockWidgetPB.setTitleBarWidget(tWidget)
    dockArea = getConfigDockArea()

    existing_widgets = [widget for widget in mw.findChildren(QDockWidget) if mw.dockWidgetArea(widget) == dockArea]

    mw.addDockWidget(dockArea, dockWidgetPB)

    if len(existing_widgets) > 0:
        mw.setDockNestingEnabled(True)

        if dockArea == Qt.DockWidgetArea.TopDockWidgetArea or dockArea == Qt.DockWidgetArea.BottomDockWidgetArea:
            stack_method = Qt.Orientation.Vertical
        if dockArea == Qt.DockWidgetArea.LeftDockWidgetArea or dockArea == Qt.DockWidgetArea.RightDockWidgetArea:
            stack_method = Qt.Orientation.Horizontal
        mw.splitDockWidget(existing_widgets[0], dockWidgetPB, stack_method)

    if qbr > 0 or pbdStyle is not None:
        mw.setPalette(palette)
    mw.web.setFocus()
    return dockWidgetPB


def check_dock_widget_area():
    global dockWidgetPB
    if isinstance(dockWidgetPB, QDockWidget):
        current_area = mw.dockWidgetArea(dockWidgetPB)
        new_dockArea = getConfigDockArea()

        if current_area != new_dockArea:
            mw.removeDockWidget(dockWidgetPB)

            existing_widgets = [widget for widget in mw.findChildren(QDockWidget) if mw.dockWidgetArea(widget) == new_dockArea]
            # existing_widgets = [widget for widget in mw.findChildren(QWidget) if mw.dockWidgetArea(widget) == new_dockArea]

            mw.addDockWidget(new_dockArea, dockWidgetPB)
            dockWidgetPB.show()

            print(existing_widgets)
            if len(existing_widgets) > 0:
                mw.setDockNestingEnabled(True)

                if new_dockArea in [Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea]:
                    stack_method = Qt.Orientation.Vertical
                elif new_dockArea in [Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea]:
                    stack_method = Qt.Orientation.Horizontal
                mw.splitDockWidget(existing_widgets[0], dockWidgetPB, stack_method)



def updatePB():
    if PB_TYPE == TYPE_A:
        updatePB_A()
    elif PB_TYPE == TYPE_B:
        updatePB_B()
    nmApplyStyle()

def updateSessionTime():
    """Updates only the session time"""
    if session_start_time is not None and progressBar_2 is not None:
        elapsed_time = (time() - session_start_time)
        session_time = format_elapsed_time(elapsed_time)
        
        #Get current text and update only the session time part
        current_text = progressBar_2.format()
        if "| Session: " in current_text:
            base_text = current_text.split("| Session: ")[0]
            new_text = f"{base_text}| Session: {session_time}"
            progressBar_2.setFormat(new_text)

def format_elapsed_time(seconds: float) -> str:
    """Format elapsed time as HH:MM:SS."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def updatePB_A():
    if currDID:
        pbMax = totalCount[currDID]
        pbValue = doneCount[currDID]
    else:
        pbMax = pbValue = 0
        for node in mw.col.sched.deck_due_tree().children:
            pbMax += totalCount[node.deck_id]
            pbValue += doneCount[node.deck_id]

    if pbMax == 0:  # 100%
        progressBar_2.setRange(0, 1)
        progressBar_2.setValue(1)
    else:
        progressBar_2.setRange(0, pbMax)
        progressBar_2.setValue(pbValue)

    output = ""
    if showNumber:
        if showPercent:
            percent = 100 if pbMax == 0 else int(100 * pbValue / pbMax)
            output = "%d / %d (%d%%)" % (pbValue, pbMax, percent)
        else:
            output = "%d / %d" % (pbValue, pbMax)

    from .time_left import estimateTimeLeft
    output += estimateTimeLeft(pbMax-pbValue)

    # Add card speed calculation
    if session_start_time is not None:  # Ensure session_start_time is initialized
        elapsed_time = (time() - session_start_time)  # in seconds
        if cards_done_in_session == 0:
            card_speed = " | Calculating..."  # Display if no cards have been reviewed yet'
            estimated_completion_time = None
        else:
            card_speed = f" | {elapsed_time / cards_done_in_session:.1f} sec/card"  # Seconds per card
            time_etc = (elapsed_time / cards_done_in_session) * (pbMax - pbValue)
            estimated_completion_time = time() + time_etc

        output += card_speed
        if estimated_completion_time:
            etc_str = datetime.fromtimestamp(estimated_completion_time).strftime("%H:%M:%S")
            output += f" ({etc_str} ETC)"
        else:
            output += " (ETC Calculating...)"

        # Add review session time
        session_time = format_elapsed_time(elapsed_time)  # Format elapsed time as HH:MM:SS
        output += f" | Session: {session_time}"  # Append session time to the output
    progressBar_2.setFormat(output)

def start_session_timer():
    global session_timer

    # Create a QTimer to update time
    session_timer = QTimer()
    session_timer.timeout.connect(updateSessionTime)
    session_timer.start(500)

def stop_session_timer():
    global session_timer

    if session_timer:
        session_timer.stop()
        session_timer = None

#----------------------------
def updatePB_B():
    # Get studied cards  and true retention stats. TODAY'S VALUES
    a = (mw.col.sched.day_cutoff - 86400) * 1000

    cards = mw.col.db.first("""
    select
    sum(case when ease >=1 then 1 else 0 end) /* cards */
    from revlog where id > ? """, a)
    # cards = cards[0] if cards else 0
    cards = cards[0] if cards and cards[0] is not None else 0

    pbMax = pbValue = 0

    # Sum top-level decks
    for node in mw.col.sched.deck_due_tree().children:
        pbMax += totalCount[node.deck_id]
        pbValue += doneCount[node.deck_id]

    var_diff = pbMax - pbValue
    progbarmax = int(var_diff + cards)

    if pbMax == 0:  # 100%
        progressBar_2.setRange(0, 1)
        progressBar_2.setValue(1)
    else:
        progressBar_2.setRange(0, progbarmax)
        progressBar_2.setValue(cards)

    # if showNumber:
    #     if showPercent:
    #         percent = 100 if pbMax == 0 else int(100 * pbValue / pbMax)
    #         progressBar_2.setFormat("%d / %d (%d%%)" % (pbValue, pbMax, percent))
    #     else:
    #         progressBar_2.setFormat("%d / %d" % (pbValue, pbMax))

    percent = 100 if pbMax == 0 else (100 * cards / progbarmax)
    percentdiff = (100 - percent)

    output = ""
    if showNumber:
        if showPercent:
            output = f"{cards} ({percent:.0f}%) done"
            output += f" / {var_diff:.0f} ({percentdiff:.0f}%) left"
        else:
            output = f"{cards} done"
            output += f" / {var_diff:.0f} left"

    from .time_left import estimateTimeLeft
    output += estimateTimeLeft(var_diff)
    progressBar_2.setFormat(output)


#----------------------------

def setScrollingPB() -> None:
    progressBar_2.setRange(0, 0)
    if showNumber:
        progressBar_2.setFormat("Waiting...")


def nmApplyStyle() -> None:
    # mw.setStyleSheet(
    #         '''
    # QMainWindow::separator
    # {
    #     width: 2px;
    #     height: 2px;
    #     background-color: transparent;
    # }
    # ''')
    mw.setStyleSheet(
            '''
    QMainWindow::separator
    {
        width: 2px;
        height: 2px;
    }
    ''')

def calcProgress(rev: int, lrn: int, new: int) -> int:
    ret = 0
    if includeRev:
        ret += rev * revWeight
    if includeLrn:
        ret += lrn * lrnWeight
    if includeNew or (includeNewAfterRevs and rev == 0):
        ret += new * newWeight
    return ret

def updateCountsForAllDecks(updateTotal: bool) -> None:
    for node in mw.col.sched.deck_due_tree().children:
        updateCountsForTree(node, updateTotal)

def updateCountsForTree(node, updateTotal: bool) -> None:
    did = node.deck_id
    remain = calcProgress(node.review_count, node.learn_count, node.new_count)

    updateCountsForDeck(did, remain, updateTotal)

    for child in node.children:
        updateCountsForTree(child, updateTotal)

def updateCountsForDeck(did: int, remain: int, updateTotal: bool):
    if did not in totalCount.keys():
        totalCount[did] = remainCount[did] = remain
        doneCount[did] = 0
    else:
        remainCount[did] = remain
        if updateTotal:
            totalCount[did] = doneCount[did] + remainCount[did]
        else:
            if remainCount[did] + doneCount[did] > totalCount[did]:
                if forceForward:
                    pass
                else:
                    totalCount[did] = doneCount[did] + remainCount[did]
            else:
                doneCount[did] = totalCount[did] - remainCount[did]

def afterStateChangeCallBack(state: str, oldState: str) -> None:
    global currDID, session_start_time, cards_done_in_session

    if state == "resetRequired":
        if scrollingBarWhenEditing:
            setScrollingPB()
        return
    elif state == "deckBrowser":
        if not progressBar_2 or didConfigChange():
            initPB()
            updateCountsForAllDecks(True)
        currDID = None
        stop_session_timer()
        session_start_time = None
    elif state == "overview":
        if not progressBar_2 or didConfigChange():
            initPB()
            updateCountsForAllDecks(True)
        currDID = mw.col.decks.current()['id']
        stop_session_timer()
        session_start_time = None
    elif state == "profileManager":
        return
    else:
        if state == "review":
            session_start_time = time()  # Initialize session start time
            cards_done_in_session = 0  # Reset cards done in the current session
            start_session_timer()  # Start the session timer when entering review mode
        currDID = mw.col.decks.current()['id']

    updateCountsForAllDecks(True)
    updatePB()

def showQuestionCallBack(*args,**kwargs) -> None:
    global cards_done_in_session  # Add cards_done_in_session to the global declaration
    cards_done_in_session += 1  # Increment cards done in the current session
    updateCountsForAllDecks(False)
    updatePB()

gui_hooks.state_did_change.append(afterStateChangeCallBack)
gui_hooks.reviewer_did_show_question.append(showQuestionCallBack)


def after_change_shige_settings(state: str) -> None:
    global currDID
    did_confing_change = didConfigChange()

    if state == "resetRequired":
        if scrollingBarWhenEditing:
            setScrollingPB()
        return
    elif state == "deckBrowser":
        if not progressBar_2 or did_confing_change:
            initPB()
            updateCountsForAllDecks(True)
        currDID = None
    elif state == "profileManager":
        return
    else:  # "overview" or "review"
        initPB()
        currDID = mw.col.decks.current()['id']

    updateCountsForAllDecks(True)
    updatePB()
    hide_progressbar()
    check_dock_widget_area()

def hide_progressbar(*args,**kwargs):
    global progressBar_2
    config = mw.addonManager.getConfig(__name__)
    progressBar_2.setVisible(not config.get("hide_Progressbar", False))

gui_hooks.main_window_did_init.append(hide_progressbar)