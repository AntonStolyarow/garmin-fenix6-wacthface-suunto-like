import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

class SuuntoLikeApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state) {
    }

    function onStop(state) {
    }

    function getInitialView() {
        return [ new SuuntoLikeView() ];
    }
}
