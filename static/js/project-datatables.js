// Call the dataTables jQuery plugin
$(document).ready(function() {
    $('#dataTable').DataTable({
        "pageLength": 50,
        "lengthMenu": [
            [20, 50, 100, 250, -1],
            [20, 50, 100, 250, "All"]],
          "columnDefs": [
              { "targets": 0, "type": "html" }
          ],
         "dom": '<"top"i>rt<"bottom"flp><"clear">'
    });
});
