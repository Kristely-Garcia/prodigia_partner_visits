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
                
                var visit_ids = [];
                var line_ids = this.recordData.line_ids.data;
                //var partner_ids = [];
                for(var x=0;x<line_ids.length;x++){
                  console.log(line_ids[x].data);
                  console.log(line_ids[x].data.name);
                  visit_ids.push(line_ids[x].data.name);
                }
                console.log("visit_ids: "+visit_ids)
                domain = [['id','in',visit_ids]];
              break;
          }
          this._rpc({ 
              model: 'partner.visit', 
              method: 'search_read', 
              fields: ['name','display_name','lat1','lng1','lat2','lng2','lat_partner','lng_partner','date','end_date','partner_display_name','visit_duration'], 
              domain: domain,
          }) 
          .then(function(records) 
          { 
              // Create a map object and specify the DOM element
              // for display.
              console.log("222222222222")
              var map = new google.maps.Map(map_canvas, {
                center: {lat: 29.0894152,lng: -110.9612378},
                zoom: 13
              });

              for(var x=0;x<records.length;x++){
                var lat_partner = records[x].lat_partner;
                var lng_partner = records[x].lng_partner;
                var lat1 = records[x].lat1;
                var lng1 = records[x].lng1;
                var lat2 = records[x].lat2;
                var lng2 = records[x].lng2;
                var visit = String(records[x].name);
                var date = String(records[x].date);
                var end_date = String(records[x].end_date);
                var partner_display_name = String(records[x].partner_display_name);
                var visit_duration = String(records[x].visit_duration);

                //var partner_name = records[x].display_name
                var partnerLatLng = {lat: lat_partner, lng: lng_partner};
                var myLatLng1 = {lat: lat1, lng: lng1};
                var myLatLng2 = {lat: lat2, lng: lng2};

                //punto inicio de visita
                console.log("partner_display_name "+partner_display_name);
                if(partner_display_name != "false"){
                  console.log("333333");
                  var partner_marker;
                  var partner_title = "Visita: "+visit+"\nCliente: "+partner_display_name;
                  partner_marker = new google.maps.Marker({
                    map: map,
                    position: partnerLatLng,
                    title: partner_title
                  });
                  partner_marker.setIcon('https://maps.google.com/mapfiles/ms/icons/red-dot.png');
                }

                //punto inicio de visita
                console.log("date "+date);
                if(date != "false"){
                  console.log("44444");
                  var titulo_inicio = "Visita: "+visit+"\nInicio de visita: "+date+"\nCliente: "+partner_display_name;
                  var marker;
                  console.log(typeof  titulo_inicio);
                  marker = new google.maps.Marker({
                    map: map,
                    position: myLatLng1,
                    title: String(titulo_inicio)
                  });
                  marker.setIcon('https://maps.google.com/mapfiles/ms/icons/green-dot.png');
                }
                
                //punto final
                console.log("end_date "+end_date);
                if(end_date != "false"){
                  console.log("55555");
                  var marker2;
                  var titulo_fin = "Visita: "+visit+"\nFin de visita: "+date+"\nCliente: "+partner_display_name+"\nDuracion: "+visit_duration+" mins.";
                  console.log(typeof  titulo_fin);
                  marker2 = new google.maps.Marker({
                    map: map,
                    position: myLatLng2,
                    title: titulo_fin
                  });
                  marker2.setIcon('https://maps.google.com/mapfiles/ms/icons/yellow-dot.png');
                }
                
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
