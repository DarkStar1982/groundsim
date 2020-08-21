//  use vue.js

$(document).ready(function () {
    $(".mission_type").hide();
    $("#sel_mission_type").change(function () {
        var missionType = $(this).find('option:selected').val();
        switch (missionType) {
            case "1":
                $(".mission_type").hide();
                $("#earth_mission").show();
                break;
            case "2":
                $(".mission_type").hide();
                $("#sdr_mission").show();
                break;
            case "3":
                $(".mission_type").hide();
                $("#fire_mission").show();
                break;
            case "4":
                $(".mission_type").hide();
                $("#custom_mission").show();
                break;
            default:
                $(".mission_type").hide();
                break;
        }
    })

});
