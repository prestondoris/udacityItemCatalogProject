/*
$('#update').submit(function(event){
    event.preventDefault()
    var $form = $(this);
    var $name = $form.find('input[name=name]').val();
    var $url = $form.att('action')
    var data = {
        name: $name
    }
    $.ajex({
        type: "post",
        url: $url,
        data: data,
        dataType: json,
        contentType: 'application/json',
        success: function(result) {
            console.log("POST request sent");
        }
        error: fucntion(result) {
            console.log("POST request failed");
        }
    })
});
*/
console.log("connected") 
var $beerInfo = $(.beerInfo);

$(.beerInfo).click(function() {
    this.addClass('active');
});
