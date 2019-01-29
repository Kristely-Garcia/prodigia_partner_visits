/*
para que este widget sea reconocido, es necesario
agregarlo en el archivo views/templates.xml
sintaxis:
<template id="assets_backend" inherit_id="web.assets_backend"> 
    <xpath expr="." position="inside"> 
        <script
            src="/prodigia_partner_visits/static/src/js/button_widget.js"
            type="text/javascript"
        /> 
    </xpath> 
</template> 
*/

odoo.define('prodigia_partner_visits.location_buttons_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;


var LocationButtonsWidget = AbstractField.extend({
    // tipos de campo en lso que se puede usar este widget
    supportedFieldTypes: ['char'],

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @returns {boolean}
     */
    isSet: function() {
        return true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @override
     render es la funcion que dibuja el widget
     */
    _render: function() {
        var self = this;
        /*VisitButtons debe estar definido en la carpeta
        xml/js_qweb_templates.xml
        es un qweb donde se define el html del widget
        */
        //this.recordData[] permite acceder a los valores de los campos del record actual
        //console.log(this.recordData)
        this.$el.html(QWeb.render('VisitButtons', {
            //this.res_id es el id del record actual
            visit_id: this.res_id,
            state: this.recordData['state']
        })); 
        //se agrega evento a boton
        //$el representa el root element html
        //find es una funcion jquery que sirve para seleccionar un elemento html
        this.$el.find('.js_get_current_location').on('click', self._onClickButton.bind(self));
        this.$el.find('.js_get_current_location2').on('click', self._onClickButton.bind(self));
    },
    //render end

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    /*
    se utilizara una funcion callback,
    para obtener los valores de lat y lng
    del metodo asincrono navigator.geolocation.getCurrentPosition
    */
    _onClickButton: function (event) {
        console.log("_onClickButton");
        //var self = this;

        this._getLocation(function (pos,self) {
            console.log("_onVisit");
            console.log(self);
            //var self = this;
            var visitId = self.res_id;
            var state = self.recordData['state'];
            var odoo_method;

            //se obtiene punto actual (lat, lng)
            //var pos = self._getLocation();
            var distance = 0.0;
            console.log('pos: '+pos);
            console.log('distance: '+distance);

            if (state == 'nuevo') {
                odoo_method = 'visit_start';
            } else {
                odoo_method = 'visit_end';

                //se obtiene posicion de incicio de visita:
                var lat1 = self.recordData['lat1'];
                var lng1 = self.recordData['lng1'];
                var pos1 = {lat: lat1, lng: lng1}
                //si es el boton de finalizar, se calcula distancia entre
                //los el punto inicial y final
                distance =  self._getDistance(pos,pos1);
            }

            /*
            this._rpc realiza una llamada a python
            para ejecutar un metodo, atributos:
            -model: modelo de odoo
            -method: metodo a ejecutar
            */
            console.log('!!!!');
            try{
                self._rpc({
                    model: 'partner.visit',
                    method: odoo_method,
                    //en args, el primer argumento equivale a self en python, por lo que tiene que ser el id
                    //el segundo argumento es el contexto que se debera sacar con self.env.context
                    args: [self.res_id,{'lat': pos.lat,'lng': pos.lng,'distance': distance}]
                }).then(function () {
                    //desencadena una recarga de pagina
                    self.trigger_up('reload');
                });
            }catch(err) {
                alert("Es necesario activar permisos de ubicacion en su navegador!");
            }


        },this); //end of callback
        console.log("END")
    },


    //--------------------------------------------------------------------------
    // Other functions
    //--------------------------------------------------------------------------

    /*
    Obtiene lattitud y longitud del navegador
    */
    _getLocation: function (callback,self) {
        console.log("_getLocation");
        var pos = {
          lat: 29.09737,
          lng: -111.02102
        };
        callback(pos,self);
        return true;
        /*lat: 29.09737,
        lng: -111.02102*/

        try {
            console.log("obtener coordenadas de navegador...");
            //if (navigator.geolocation) {
            console.log("aaaa");
            navigator.geolocation.getCurrentPosition(function(position) {
                console.log("wwwww");
                var pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                console.log("pos1111: "+pos);
                callback(pos,self);
                console.log("end callback");
                //return pos;
            });
            //}
        }
        catch(err) {
            alert("Es necesario activar permisos de ubicacion en su navegador!");
        }

    }, // _getLocation end



    _rad: function(x) {
        /*
        calcula el radio
        */
        return x * Math.PI / 180;
    },

    _getDistance: function(p1, p2) {
        /*
        obtiene la distancia entre 2 puntos en metros
        y la devuelve
        */
        try{
            var self = this;
            var R = 6378137; // Earth’s mean radius in meter
            var dLat = self._rad(p2.lat - p1.lat);
            var dLong = self._rad(p2.lng - p1.lng);
            var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(self._rad(p1.lat)) * Math.cos(self._rad(p2.lat)) *
                Math.sin(dLong / 2) * Math.sin(dLong / 2);
            var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            var d = R * c;
            return d; // returns the distance in meter
        }
        catch(err) {
            alert("Es necesario activar permisos de ubicacion en su navegador!");
        }
        
    },

});
//se agrega widget al registro
field_registry.add('location_buttons_widget', LocationButtonsWidget);

});
