/*
CONVIERTE CAMPO DE RES_PARTNER
EN MAPA
LEE LA LAT Y LONG REGISTRADOS EN EL PARTNER
Y CREA UN MARCADOR
*/
odoo.define('prodigia_gmap_widget.gmap_widget', function(require){ 
    var registry = require('web.field_registry'), 
    AbstractField = require('web.AbstractField');

    var Gmap = AbstractField.extend({
        className: 'oe_form_field_many2one_gmap',
        template: 'Gmap',

        start: function(){

          map_canvas = this.$('#map-canvas')[0]
          /*console.log(this)*/
          var deferred = new jQuery.Deferred(), 
          self = this;
          /*var domain = this.field.domain;*/
          var field_type = this.field.type;
          var domain;
          switch(field_type){
            case "many2one":
                var partner_id = this.value.res_id;
                domain = [['id','=',partner_id]];
              break;
            default:
                var line_ids = this.recordData.line_ids.data
                var partner_ids = [];
                for(var x=0;x<line_ids.length;x++){
                  partner_ids.push(line_ids[x].data.partner_id.data.id)
                }
                domain = [['id','in',partner_ids]];
              break;
          }
          this._rpc({ 
              /*model: this.field.relation,*/
              model: 'res.partner', 
              method: 'search_read', 
              fields: ['display_name','partner_latitude','partner_longitude'], 
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
                var lat = records[x].partner_latitude
                var lng = records[x].partner_longitude
                var partner_name = records[x].display_name
                var myLatLng = {lat: lat, lng: lng};
                
                
                // Create a marker and set its position.
                var marker = new google.maps.Marker({
                  map: map,
                  position: myLatLng,
                  title: partner_name
                });
              }
              deferred.resolve(); 
          });

          return jQuery.when( 
              /*this._super.apply(this, arguments), */
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
