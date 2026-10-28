import Toybox.Graphics;
import Toybox.Lang;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class SuuntoLikeView extends WatchUi.WatchFace {

    // Цвета: чёрный фон, всё остальное белым
    private const BG = Graphics.COLOR_BLACK;
    private const FG = Graphics.COLOR_WHITE;

    // Промежуток между символами в шрифтах, px.
    // Должен совпадать с gap * cell в tools/dotfont.py
    private const GAP_PX = 6;        // время и секунды: 2 колонки по 3 px
    private const GAP_SMALL_PX = 6;  // дата: 2 колонки по 3 px

    // Отступы раскладки (те же, что в tools/preview.py)
    private const SEC_GAP = 6;   // между минутами и секундами
    private const DATE_GAP = 26; // между датой и временем

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

        var clock = System.getClockTime();
        var timeStr = formatHour(clock.hour) + clock.min.format("%02d");
        var secStr = clock.sec.format("%02d");

        var bigH = dc.getFontHeight(_bigFont);
        var smallH = dc.getFontHeight(_smallFont);
        _secH = dc.getFontHeight(_secFont);

        // Время + секунды центрируются как одна группа по ширине,
        // а дата + время - по высоте экрана
        var timeW = inkWidth(dc, timeStr, _bigFont);
        _secW = inkWidth(dc, secStr, _secFont);
        var groupW = timeW + SEC_GAP + _secW;
        var tx = (w - groupW) / 2;
        var blockH = smallH + DATE_GAP + bigH;
        var dy = (h - blockH) / 2;
        var ty = dy + smallH + DATE_GAP;

        dc.setColor(FG, Graphics.COLOR_TRANSPARENT);

        // Дата над временем: "Wed 28.10"
        drawCentered(dc, w, dy, _smallFont, formatDate());

        dc.drawText(tx, ty, _bigFont, timeStr, Graphics.TEXT_JUSTIFY_LEFT);

        // Секунды выровнены по нижнему краю минут
        _secX = tx + timeW + SEC_GAP;
        _secY = ty + bigH - _secH;
        dc.drawText(_secX, _secY, _secFont, secStr, Graphics.TEXT_JUSTIFY_LEFT);
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

    private function drawCentered(dc, w, y, font, text) {
        var x = (w - inkWidth(dc, text, font)) / 2;
        dc.drawText(x, y, font, text, Graphics.TEXT_JUSTIFY_LEFT);
    }

    // Ширина строки без хвостового промежутка после последнего символа
    private function inkWidth(dc, text, font) {
        var gap = (font == _smallFont) ? GAP_SMALL_PX : GAP_PX;
        return dc.getTextWidthInPixels(text, font) - gap;
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
}
