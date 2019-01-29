/*
CONVIERTE CAMPO DE RES_PARTNER
EN MAPA
LEE LA LAT Y LONG REGISTRADOS EN EL PARTNER
Y CREA UN MARCADOR
*/
odoo.define('prodigia_partner_visits.gmap_widget', function(require){ 
    var registry = require('web.field_registry'), 
    AbstractField = require('web.AbstractField');

    var Gmap = AbstractField.extend({
        className: 'oe_form_field_many2one_gmap',
        template: 'Gmap',

        start: function(){

          map_canvas = this.$('#map-canvas')[0]
          var deferred = new jQuery.Deferred(), 
          self = this;
          console.log(this)
          var field_type = this.field.type;
          var domain;
          switch(field_type){
            case "many2one":
                var visit_id = this.res_id;
                domain = [['id','=',visit_id]];
              break;
            default:
                var visit_ids = this.recordData.line_ids.res_ids;
                /*var partner_ids = [];
                for(var x=0;x<line_ids.length;x++){
                  partner_ids.push(line_ids[x].data.partner_id.data.id)
                }*/
                domain = [['id','in',visit_ids]];
              break;
          }
          this._rpc({ 
              model: 'partner.visit', 
              method: 'search_read', 
              fields: ['display_name','lat1','lng1','lat2','lng2'], 
              domain: domain,
          }) 
          .then(function(records) 
          { 
              // Create a map object and specify the DOM element
              // for display.
              var map = new google.maps.Map(map_canvas, {
                center: {lat: 29.0894152,lng: -110.9612378},
                zoom: 13
              });

              for(var x=0;x<records.length;x++){
                var lat1 = records[x].lat1
                var lng1 = records[x].lng1
                var lat2 = records[x].lat2
                var lng2 = records[x].lng2

                //var partner_name = records[x].display_name
                var myLatLng1 = {lat: lat1, lng: lng1};
                var myLatLng2 = {lat: lat2, lng: lng2};
                
                
                //punto inicio de visita
                var marker = new google.maps.Marker({
                  map: map,
                  position: myLatLng1,
                  //title: partner_name
                });
                //punto final
                var marker2 = new google.maps.Marker({
                  map: map,
                  position: myLatLng2,
                  //title: partner_name
                });
              }
              deferred.resolve(); 
          });

          return jQuery.when( 
              deferred 
          ); 
        },

        _render: function(){
          this.renderElement();
        },
    });
    registry.add('g_map', Gmap);
    return { 
        Gmap: Gmap, 
    }
});
