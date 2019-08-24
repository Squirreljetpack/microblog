$( function() {
    var $uploadCrop;
    target=document.getElementById("InputArea")
    target.addEventListener("dragover", function(event) {
        event.preventDefault();
    }, false);

    target.addEventListener("drop", function(event) {

        event.preventDefault();
        wrapper(event.dataTransfer)


    }, false);

    $('#left').on('click', function () { 
        if ($uploadCrop) $uploadCrop.croppie('rotate', 90)
    })
    $('#right').on('click', function () { 
        if ($uploadCrop) $uploadCrop.croppie('rotate', -90)
    })

    function readFile(file) {   
        if ($uploadCrop) $uploadCrop.croppie('destroy')
        var reader = new FileReader();          
        reader.onload = function (e) {
            $uploadCrop = $('#upload-demo').croppie({
                mouseWheelZoom: false,
                enableOrientation: true,
                viewport: {
                    width: 256,
                    height: 256,
                    type: 'square'
                },
                boundary: {
                    width: $("#upload-demo").parent().width(),
                    height: $("#upload-demo").parent().width()
                }
            });

            $uploadCrop.croppie('bind', {
                url: e.target.result
            });
        }           
        reader.readAsDataURL(file);
    }
    

    function wrapper(input) {
        if (input.files && input.files[0]) {
            readFile(input.files[0]);
            $('#myModal').modal('show');
            $('#myModal').modal('handleUpdate')
            $('#ChooseFileLabel').text(input.files[0].name);
        }


    }

    $('#myModal').modal({ show: false})
    $('#upload').on('change', function () { 
        wrapper(this)
    });

    $('#saveImage').on('click', function (ev) {
        $('#myModal').modal('hide')
        $uploadCrop.croppie('result', {
            type: 'base64',
            size: {width: 256, height: 256}
        }).then(function (resp) {
            $('#my_avatar').val(resp);
            img     = new Image();
            context = document.getElementById("mycanvas").getContext("2d")
            img.src = resp;
            img.onload = function() {
                context.drawImage(img, dy=0, dx=0, dWidth=256, dWidth=256);
                $('#mycanvas').addClass('border')
            };
        });
    });
});