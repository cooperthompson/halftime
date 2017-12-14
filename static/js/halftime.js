/**
 * Created by cooper on 12/13/2017.
 */


$(function() {

  $('.datepicker').datepicker();


  $("#game_date_selector").change(function() {
    this.submit();
  });
});