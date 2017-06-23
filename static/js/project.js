(function($) {
    "use strict"; // Start of use strict

    // Scroll to top button appear
    $(document).scroll(function() {
        var scrollDistance = $(this).scrollTop();
        if (scrollDistance > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });

    // Smooth scrolling using jQuery easing
    $(document).on('click', 'a.scroll-to-top', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top)
        }, 1000, 'easeInOutExpo');
        event.preventDefault();
    });

    // Call the dataTables jQuery plugin
    $(document).ready(function() {
        $('#dataTable').DataTable({
            "lengthMenu": [
                [20, 50, 100, 250, -1],
                [20, 50, 100, 250, "All"]],
              "columnDefs": [
                  { "targets": 0, "type": "html" }
              ],
             "dom": '<"top"i>rt<"bottom"flp><"clear">'
        });
    });


})(jQuery); // End of use strict

// Chart.js scripts
// -- Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';
