$(document).ready(function (){

    $('.increment-btn').click(function (e){
        e.preventDefault();

        const inc_value = $(this).closest('.product_data').find('.qty-input').val();
        let value = parseInt(inc_value, 10);
        value = isNaN(value) ? 0 : value;
        if (value < 10)
        {
            value ++;
            $(this).closest('.product_data').find('.qty-input').val();
        }
    });
});