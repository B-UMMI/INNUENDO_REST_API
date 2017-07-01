innuendoApp.controller("protocolsCtrl", function($scope, $http) {

	$scope.protocol_type = {};
	$scope.protocols_of_type = [];
	$scope.protocolTypeParameters = {};

	var protocols_list = new Protocol_List($http);

	var usedSoftware = ["INNUca", "chewBBACA", "PathoTyping"];

	$scope.loadProtocols = function(){
		$scope.getProtocolTypes();
	}

	$scope.getProtocolTypes = function(){

		protocols_list.get_protocol_types(function(results){
			$scope.protocol_types = results.protocol_types;
			options="";
			for(x in results.protocol_types){
				options +="<option>"+results.protocol_types[x]+"</option>";
			}
			$("#protocol_type_selector").append(options);
			$("#protocol_type_selector_load").append(options);
			$(".selectpicker").selectpicker({});
			
			$("#protocol_type_selector").on("change", function(){
				$scope.loadProtocolCreator($("#protocol_type_selector option:selected").text());
			});
			$("#protocol_type_selector_load").on("change", function(){
				$scope.loadProtocolType($("#protocol_type_selector_load option:selected").text());
			});
		});
	}

	$scope.addProtocol = function(){

		protocols_list.add_protocol(function(results){
			console.log(results.message);
		});

	}

	$scope.loadProtocolCreator = function(selectedType){

		$("#new_protocol_form").css({"display":"none"});

		protocols_list.load_protocol_form(selectedType, function(results){
			$(".to_empty").val("");
			$('.to_empty option').remove();
			$(".selectpicker").selectpicker("refresh");
	    	$scope.protocol_parameters = results.protocol_parameters;
	    	$scope.protocol_type = results.protocol_type;
	    	$("#create_protocol_button").css({"display":"block"});

	    	setTimeout(function(){
	    		if($.inArray("used Software", results.protocol_parameters)){
		    		options = "";
		    		for(x in usedSoftware){
		    			options += "<option>"+usedSoftware[x]+"</option>";
		    		}
		    		$('#select_software').empty();
		    		$('#select_software').append(options);
		    		$(".selectpicker").selectpicker({});
		    		$("#new_protocol_form").css({"display":"block"});
		    	}
	    	}, 600);
		});
	}

	$scope.loadProtocolType = function(selectedType){

		protocols_list.get_protocols_of_type(selectedType, function(results){
			$scope.property_fields = results.property_fields;
	    	$scope.protocols_of_type = results.protocols_of_type;
		});
	}

	$scope.loadProtocol = function(selectedProtocol){

		protocols_list.load_protocol(selectedProtocol, function(results){
			$scope.selected_protocol = results.protocol;
		});

	}

	$scope.getProtocolFields = function(uri){

		protocols_list.get_protocol_fields(uri, function(results){
			console.log(results);
			$scope.property_fields = results.property_fields.reverse();
		});
	}

	$scope.removeSelectedParameter = function(){

		var selected_text = $("#parameter_select option:selected").text();
		new_options = "";
		protocols_list.get_current_protocol_type(function(results){
			var currentProtocolType = results.currentProtocolType;
			for(x in $scope.protocolTypeParameters[currentProtocolType]){
				to_check = $scope.protocolTypeParameters[currentProtocolType][x][0].value+":"+$scope.protocolTypeParameters[currentProtocolType][x][1].value;
				if(to_check != selected_text){
					new_options += "<option>"+to_check+"</option>";
				}
			}
			$('#parameter_select').empty();
			$("#parameter_select").append(new_options);
			$(".selectpicker").selectpicker("refresh");
		});

	}

	$scope.AddParameters = function(){

		protocols_list.get_current_protocol_type(function(results){
			var parameterObject = $('#new_data_form').serializeArray();
			var currentProtocolType = results.currentProtocolType;
			if (!$scope.protocolTypeParameters.hasOwnProperty(currentProtocolType)){
				$scope.protocolTypeParameters[currentProtocolType] = [];
			}
			$scope.protocolTypeParameters[currentProtocolType].push(parameterObject);
			$scope.protocol_parameters = $scope.protocolTypeParameters[currentProtocolType];

			option = "";
			for(x in $scope.protocolTypeParameters[currentProtocolType]){
				option += "<option>"+$scope.protocolTypeParameters[currentProtocolType][x][0].value+":"+$scope.protocolTypeParameters[currentProtocolType][x][1].value+"</option>";
			}

			$('#parameter_select').empty();
			$("#parameter_select").append(option);
			$(".selectpicker").selectpicker("refresh");

		});

	}


});