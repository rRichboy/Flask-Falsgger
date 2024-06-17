from flask import request, jsonify
from flask import Blueprint
import models

routes = Blueprint('routes', __name__)


# sensors
@routes.route('/sensor', methods=['GET'])
def get_sensors():
    sensors = models.get_all_sensors()
    return jsonify(sensors)


@routes.route('/sensor/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    sensor = models.get_sensor(sensor_id)
    if sensor is None:
        return jsonify({'error': 'Sensor not found'}), 404
    return jsonify(sensor)


@routes.route('/sensor', methods=['POST'])
def create_sensor():
    data = request.get_json()
    if 'sensor_name' not in data:
        return jsonify({'error': 'sensor_name is required'}), 400
    if 'sensors_measurements' not in data:
        return jsonify({'error': 'sensors_measurements is required'}), 400

    sensor_name = data['sensor_name']
    measurements = data['sensors_measurements']
    sensor_id = models.create_sensor(sensor_name, measurements)
    sensor = models.get_sensor(sensor_id)
    return jsonify(sensor), 201


@routes.route('/sensor/update/<int:sensor_id>', methods=['PUT'])
def update_sensor_by_id(sensor_id):
    data = request.get_json()
    sensor_name = data.get('sensor_name')
    updated_sensor = models.update_sensor(sensor_id, sensor_name)
    if updated_sensor is None:
        return jsonify({'error': 'Sensor not found or no changes were made'}), 404
    return jsonify(updated_sensor)


@routes.route('/sensor/delete/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    sensor = models.get_sensor(sensor_id)
    if sensor is None:
        return jsonify({'error': 'Sensor not found'}), 404
    models.delete_sensor(sensor_id)
    return '', 204


@routes.route('/sensor/<int:sensor_id>/type', methods=['GET'])
def get_sensor_types(sensor_id):
    sensor_types = models.get_sensor_types(sensor_id)
    if not sensor_types:
        return jsonify({'error': 'No sensor types found for this sensor'}), 404
    return jsonify(sensor_types)


# measurment types
@routes.route('/measurement_type', methods=['GET'])
def get_measurement_types():
    measurement_types = models.get_all_measurement_types()
    return jsonify(measurement_types)


@routes.route('/measurement_type', methods=['POST'])
def create_measurement_type_route():
    data = request.get_json()
    if 'name' not in data or 'units' not in data:
        return jsonify({'error': 'name and units are required'}), 400
    measurement_type_id = models.create_measurement_type(data['name'], data['units'])
    measurement_type = {'id': measurement_type_id, 'name': data['name'], 'units': data['units']}
    return jsonify(measurement_type), 201


@routes.route('/measurement_type/<int:type_id>', methods=['PUT'])
def update_measurement_type_route(type_id):
    data = request.get_json()
    if 'name' not in data or 'units' not in data:
        return jsonify({'error': 'Name and units are required'}), 400

    name = data['name']
    units = data['units']
    models.update_measurement_type(type_id, name, units)
    return '', 200


@routes.route('/measurement_type/<int:type_id>', methods=['DELETE'])
def delete_measurement_type_route(type_id):
    models.delete_measurement_type(type_id)
    return '', 204


# meteostations
@routes.route('/meteostation', methods=['GET'])
def get_meteostations():
    meteostations = models.get_all_meteostations()
    return jsonify(meteostations)


@routes.route('/meteostation/<int:station_id>', methods=['GET'])
def get_meteostation(station_id):
    meteostation = models.get_meteostation(station_id)
    if meteostation is None:
        return jsonify({'error': 'Meteostation not found'}), 404
    return jsonify(meteostation)


@routes.route('/meteostation', methods=['POST'])
def create_meteostation():
    data = request.get_json()
    if not all(key in data for key in ('name', 'longitude', 'latitude')):
        return jsonify({'error': 'Name, longitude, and latitude are required'}), 400
    station_id = models.create_meteostation(data['name'], data['longitude'], data['latitude'])
    meteostation = models.get_meteostation(station_id)
    return jsonify(meteostation), 201


@routes.route('/meteostation/<int:station_id>', methods=['PUT'])
def update_meteostation(station_id):
    data = request.get_json()
    if not all(key in data for key in ('name', 'longitude', 'latitude')):
        return jsonify({'error': 'Name, longitude, and latitude are required'}), 400
    models.update_meteostation(station_id, data['name'], data['longitude'], data['latitude'])
    meteostation = models.get_meteostation(station_id)
    if meteostation is None:
        return jsonify({'error': 'Meteostation not found'}), 404
    return jsonify(meteostation)


@routes.route('/meteostation/<int:station_id>', methods=['DELETE'])
def delete_meteostation_route(station_id):
    try:
        models.delete_meteostation(station_id)
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@routes.route('/meteostation/<int:station_id>/sensor', methods=['GET'])
def get_sensors_by_station_id(station_id):
    sensors = models.get_sensors_by_station_id(station_id)
    if not sensors:
        return jsonify({'error': 'No sensors found for this station'}), 404
    return jsonify(sensors)


# sensors measurements


@routes.route('/sensors_measurements/<int:sensor_id>/', methods=['POST'])
def add_sensor_measurements_route(sensor_id):
    data = request.get_json()
    if 'sensors_measurements' not in data:
        return jsonify({'error': 'sensors_measurements are required'}), 400

    try:
        models.add_sensor_measurements(sensor_id, data['sensors_measurements'])
        return '', 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@routes.route('/sensors_measurements/<int:sensor_id>/', methods=['DELETE'])
def delete_sensor_measurements_route(sensor_id):
    data = request.get_json()
    if 'measurements_type' not in data:
        return jsonify({'error': 'measurements_type is required'}), 400

    try:
        models.delete_sensor_measurements(sensor_id, data['measurements_type'])
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# meteostation sensors


@routes.route('/meteostations_sensors/', methods=['POST'])
def add_meteostation_sensors_route():
    data = request.get_json()
    if 'meteostations_sensors' not in data:
        return jsonify({'error': 'meteostations_sensors are required'}), 400

    try:
        models.add_meteostation_sensors(data['meteostations_sensors'])
        return '', 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@routes.route('/meteostations_sensors/<string:sensor_inventory_number>/removed_ts', methods=['PUT'])
def remove_meteostation_sensor_route(sensor_inventory_number):
    data = request.get_json()
    removed_ts = data.get('removed_ts')

    try:
        models.remove_meteostation_sensor(sensor_inventory_number, removed_ts)
        return '', 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@routes.route('/meteostations_sensors/', methods=['GET'])
def get_all_meteostation_sensors_route():
    try:
        sensors = models.get_all_meteostation_sensors()
        return jsonify({'meteostations_sensors': sensors}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# measurment

@routes.route('/measurements', methods=['POST'])
def add_measurements_route():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Array of measurements is required'}), 400

    try:
        models.add_measurements(data)
        return '', 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@routes.route('/measurements/all', methods=['GET'])
def get_all_measurements_route():
    try:
        measurements = models.get_all_measurements()
        return jsonify(measurements), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@routes.route('/measurements', methods=['GET'])
def get_measurements_with_conditions_route():
    meteostation = request.args.get('meteostation')
    sensors = request.args.getlist('sensors')

    try:
        measurements = models.get_measurements_with_conditions(meteostation, sensors)
        return jsonify(measurements), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
