$(document).ready(function(){

    $(".twitter-date-input").prop("disabled", true);
    $("#all_tweets").prop("checked", true);

    $("#all_tweets").change(function () {
        $(".twitter-date-input").prop("disabled", $(this).prop("checked"));
    });

});

