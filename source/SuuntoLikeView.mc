import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class SuuntoLikeView extends WatchUi.WatchFace {

    // Цвета: белый фон, всё остальное чёрным
    private const BG = Graphics.COLOR_WHITE;
    private const FG = Graphics.COLOR_BLACK;

    // Промежуток между символами в шрифтах: 2 колонки по 3 px.
    // Должен совпадать с gap * cell в tools/dotfont.py
    private const GAP_PX = 6;

    // Отступы раскладки (те же, что в tools/preview.py)
    private const SEC_GAP = 6;   // между минутами и секундами
    private const DATE_GAP = 9;  // между датой и временем
    private const ROW_GAP = 9;   // между временем, шагами и пульсом

    // Иконки лежат в мелком шрифте как отдельные символы
    private const ICON_STEPS = "@";
    private const ICON_HEART = "&";

    private var _days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    private var _bigFont;
    private var _secFont;
    private var _smallFont;

    // Где рисуются секунды (нужно для обновления раз в секунду в режиме сна)
    private var _secX = 0;
    private var _secY = 0;
    private var _secW = 0;
    private var _secH = 0;

    function initialize() {
        WatchFace.initialize();
    }

    function onLayout(dc) {
        _bigFont = WatchUi.loadResource(Rez.Fonts.BigDots);
        _secFont = WatchUi.loadResource(Rez.Fonts.SecDots);
        _smallFont = WatchUi.loadResource(Rez.Fonts.SmallDots);
    }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();

        dc.clearClip();
        dc.setColor(FG, BG);
        dc.clear();

        drawTicks(dc, w, h);

        var clock = System.getClockTime();
        var timeStr = formatHour(clock.hour) + clock.min.format("%02d");
        var secStr = clock.sec.format("%02d");

        var bigH = dc.getFontHeight(_bigFont);
        var smallH = dc.getFontHeight(_smallFont);
        _secH = dc.getFontHeight(_secFont);

        // Время + секунды центрируются как одна группа
        var timeW = inkWidth(dc, timeStr, _bigFont);
        _secW = inkWidth(dc, secStr, _secFont);
        var groupW = timeW + SEC_GAP + _secW;
        var tx = (w - groupW) / 2;
        var ty = h / 2 - bigH / 2;

        dc.setColor(FG, Graphics.COLOR_TRANSPARENT);
        dc.drawText(tx, ty, _bigFont, timeStr, Graphics.TEXT_JUSTIFY_LEFT);

        // Секунды выровнены по нижнему краю минут
        _secX = tx + timeW + SEC_GAP;
        _secY = ty + bigH - _secH;
        dc.drawText(_secX, _secY, _secFont, secStr, Graphics.TEXT_JUSTIFY_LEFT);

        // Дата над временем: "Wed 28.10"
        var dateStr = formatDate();
        var dy = ty - DATE_GAP - smallH;
        drawCentered(dc, w, dy, _smallFont, dateStr);

        // Шаги и пульс под временем
        var y1 = ty + bigH + ROW_GAP;
        drawCentered(dc, w, y1, _smallFont, ICON_STEPS + getSteps());

        var y2 = y1 + smallH + ROW_GAP;
        drawCentered(dc, w, y2, _smallFont, ICON_HEART + getHeartRate());
    }

    // Вызывается раз в секунду в режиме сна: перерисовываем только секунды
    function onPartialUpdate(dc) {
        if (_secW == 0) {
            return;
        }
        var secStr = System.getClockTime().sec.format("%02d");

        dc.setClip(_secX, _secY, _secW, _secH);
        dc.setColor(BG, BG);
        dc.fillRectangle(_secX, _secY, _secW, _secH);
        dc.setColor(FG, Graphics.COLOR_TRANSPARENT);
        dc.drawText(_secX, _secY, _secFont, secStr, Graphics.TEXT_JUSTIFY_LEFT);
        dc.clearClip();
    }

    function onEnterSleep() {
        WatchUi.requestUpdate();
    }

    function onExitSleep() {
        WatchUi.requestUpdate();
    }

    // ---------- рисование ----------

    // 12 рисок по краю, наверху две точки (North), как у Suunto Core
    private function drawTicks(dc, w, h) {
        var cx = w / 2.0;
        var cy = h / 2.0;
        var k = w / 260.0;

        dc.setColor(FG, Graphics.COLOR_TRANSPARENT);
        dc.setPenWidth(3);

        for (var i = 0; i < 12; i++) {
            if (i == 0) {
                var offsets = [-4, 4];
                for (var j = 0; j < 2; j++) {
                    var b = Math.toRadians(-90 + offsets[j]);
                    dc.fillCircle(cx + 121 * k * Math.cos(b), cy + 121 * k * Math.sin(b), 3);
                }
                continue;
            }
            var a = Math.toRadians(i * 30 - 90);
            dc.drawLine(
                cx + 116 * k * Math.cos(a), cy + 116 * k * Math.sin(a),
                cx + 126 * k * Math.cos(a), cy + 126 * k * Math.sin(a)
            );
        }
        dc.setPenWidth(1);
    }

    private function drawCentered(dc, w, y, font, text) {
        var x = (w - inkWidth(dc, text, font)) / 2;
        dc.drawText(x, y, font, text, Graphics.TEXT_JUSTIFY_LEFT);
    }

    // Ширина строки без хвостового промежутка после последнего символа
    private function inkWidth(dc, text, font) {
        return dc.getTextWidthInPixels(text, font) - GAP_PX;
    }

    // ---------- данные ----------

    private function formatHour(hour) {
        var hh = hour;
        if (!System.getDeviceSettings().is24Hour) {
            hh = hour % 12;
            if (hh == 0) {
                hh = 12;
            }
        }
        return hh.format("%02d");
    }

    private function formatDate() {
        var info = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        return _days[info.day_of_week - 1] + " " + info.day.format("%d") + "." + info.month.format("%d");
    }

    private function getSteps() {
        var info = ActivityMonitor.getInfo();
        if (info != null && info.steps != null) {
            return info.steps.toString();
        }
        return "--";
    }

    private function getHeartRate() {
        var activity = Activity.getActivityInfo();
        if (activity != null && activity.currentHeartRate != null) {
            return activity.currentHeartRate.toString();
        }
        if (ActivityMonitor has :getHeartRateHistory) {
            var sample = ActivityMonitor.getHeartRateHistory(1, true).next();
            if (sample != null && sample.heartRate != ActivityMonitor.INVALID_HR_SAMPLE) {
                return sample.heartRate.toString();
            }
        }
        return "--";
    }
}
