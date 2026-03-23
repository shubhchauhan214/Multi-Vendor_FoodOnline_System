let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" -- add your country code
        componentRestrictions: {'country': ['in', 'no']},
    })

    //function to specify what should happen when the prediction is clicked
    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged(){
    var place = autocomplete.getPlace();

    //User did not select the prediction. Reset the input field or alert()
    if(!place.geometry){
        document.getElementById('id_address').placeholder = 'Start typing...';
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    //console.log(place)
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value
    geocoder.geocode({'address': address}, function(results, status){
        // console.log('results=>', results)
        // console.log('status=>', status)
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            //console.log('lat=>', latitude)
            //console.log('long=>', longitude)

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });

    // loop through the address components and assign other address data
    // Get each component of the address from the place details,
    // and then fill-in the corresponding field on the form.
    // place.address_components are google.maps.GeocoderAddressComponent objects
    // which are documented at http://goo.gle/3l5i5Mr
    let postcode = "";

    for(const component of place.address_components){
       const componentType = component.types[0];

       switch(componentType){
           case 'country':
                $('#id_country').val(component.long_name);
                break;
           case 'administrative_area_level_1':
                $('#id_state').val(component.long_name);
                break;
           case 'locality':
                $('#id_city').val(component.long_name);
                break;
           case 'postal_code':
                postcode = component.long_name;
                //$('#id_pin_code').val(component.long_name);
                break;
       }
    }

    $('#id_pin_code').val(postcode);
}


$(document).ready(function(){
    // Add Opening Hour Functionality
    $('#add_opening_hour_btn').on('click', function(e){
        e.preventDefault();

        var day = document.getElementById('id_day').value;
        var from_hour = document.getElementById('id_from_hour').value;
        var to_hour = document.getElementById('id_to_hour').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var url = document.getElementById('add_hour_url').value;

        if(is_closed){
            is_closed_val = 'True';
        }
        else{
            is_closed_val = 'False';
        }

        if((day != '' && from_hour != '' && to_hour != '') || (day != '' && is_closed)){
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed_val,
                    'csrfmiddlewaretoken': csrf_token
                },
                success: function(response){
                    if(response.status == 'Success'){
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+ response.id +'"><td><b>'+ response.day +'</b></td><td>Closed</td><td><a href="" class="remove_hour" data-url="/vendor/opening-hours/remove/'+ response.id +'/" style="text-decoration: none; color: #ff2727;"><i class="icon-close2"></i></a></td></tr>';
                        }
                        else{
                            html = '<tr id="hour-'+ response.id +'"><td><b>'+ response.day +'</b></td><td>'+ response.from_hour + ' - '+ response.to_hour +'</td><td><a href="" class="remove_hour" data-url="/vendor/opening-hours/remove/'+ response.id +'/" style="text-decoration: none; color: #ff2727;"><i class="icon-close2"></i></a></td></tr>';
                        }
                        $('.opening_hours').append(html);
                        document.getElementById('opening_hours').reset();
                    }
                    else{
                        Swal.fire(response.message, '', 'error');
                    }
                }
            })
        }
        else{
            Swal.fire('Please fill all the details.', '', 'info');
        }

    });

    // Remove Opening Hour Functionality
    $(document).on('click', '.remove_hour', function(e){
        e.preventDefault();

        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'Success'){
                    document.getElementById('hour-' + response.id).remove()
                }
                else{
                    Swal.fire(response.message, '', 'error');
                }
            }
        })
    })

    //document ready closed
});