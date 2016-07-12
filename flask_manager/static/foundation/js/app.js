(function(){
    'use strict';
    $(document).foundation();

    $('.input-select-link').on('click', function() {
        var self = $(this);
        var field = $('#'+self.data('field'));
        var value = self.data('value');
        field.val(value);
        field[0].form.submit();
    });

    $('#select-all').on('click', function() {
        var checked = document.getElementById('select-all').checked;
        for (let checkbox of document.getElementsByName('ids')) {
            checkbox.checked = checked;
        }
    })
}());
