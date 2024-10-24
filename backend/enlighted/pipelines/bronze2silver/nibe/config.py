from pydantic_settings import BaseSettings


class NibeB2SConfig(BaseSettings):

    parameters: dict = {
        40004: {
            "bronze_parameter_name": "Current outd temp (BT1)",
            "silver_parameter_name": "outdoor_temperature",
            "value_mappings": {},
        },
        40008: {
            "bronze_parameter_name": "Supply line (BT2)",
            "silver_parameter_name": "heat_medium_flow_temperature",
            "value_mappings": {},
        },
        40012: {
            "bronze_parameter_name": "Return line (BT3)",
            "silver_parameter_name": "heat_medium_flow_return_temperature",
            "value_mappings": {},
        },
        40015: {
            "bronze_parameter_name": "Brine in (BT10)",
            "silver_parameter_name": "temperature_brine_in",
            "value_mappings": {},
        },
        40016: {
            "bronze_parameter_name": "Brine out (BT11)",
            "silver_parameter_name": "temperature_brine_out",
            "value_mappings": {},
        },
        40017: {
            "bronze_parameter_name": "Con­denser (BT12)",
            "silver_parameter_name": "temperature_condensor",
            "value_mappings": {},
        },
        40018: {
            "bronze_parameter_name": "Dis­charge (BT14)",
            "silver_parameter_name": "temperature_discharge",
            "value_mappings": {},
        },
        40019: {
            "bronze_parameter_name": "Liquid line (BT15)",
            "silver_parameter_name": "temperature_liquid_line",
            "value_mappings": {},
        },
        40022: {
            "bronze_parameter_name": "Suction gas (BT17)",
            "silver_parameter_name": "temperature_suction_gas",
            "value_mappings": {},
        },
        40033: {
            "bronze_parameter_name": "Room temp­erature (BT50)",
            "silver_parameter_name": "room_temperature",
            "value_mappings": {},
        },
        40067: {
            "bronze_parameter_name": "Average outdoor temp (BT1)",
            "silver_parameter_name": "outdoor_temperature_avg",
            "value_mappings": {},
        },
        41778: {
            "bronze_parameter_name": "Current com­pressor fre­quency",
            "silver_parameter_name": "current_compressor_frequency",
            "value_mappings": {},
        },
        41929: {
            "bronze_parameter_name": "Mode (Smart Price Adaption)",
            "silver_parameter_name": "spa_price_level",
            "value_mappings": {0: "unknown", 1: "low", 2: "normal", 3: "high"},
        },
        43009: {
            "bronze_parameter_name": "Calcu­lated supply climate system 1",
            "silver_parameter_name": "heat_medium_flow_calculated_temperatur",
            "value_mappings": {},
        },
        44270: {
            "bronze_parameter_name": "Calcu­lated cooling supply climate system 1",
            "silver_parameter_name": "cooling_medium_flow_calculated_temperature",
            "value_mappings": {},
        },
        44896: {
            "bronze_parameter_name": "Heating offset (Smart Price Adaption)",
            "silver_parameter_name": "smart_price_adaption_temperature_correction",
            "value_mappings": {},
        },
        44899: {
            "bronze_parameter_name": "Cooling offset (Smart Price Adaption)",
            "silver_parameter_name": "smart_price_adaption_cool_temperature_correction",
            "value_mappings": {},
        },
        43427: {
            "bronze_parameter_name": "Status com­pressor",
            "silver_parameter_name": "compressor_state",
            "value_mappings": {
                20: "off",
                40: "starting",
                60: "operating",
                100: "stopping",
            },
        },
        43437: {
            "bronze_parameter_name": "Heating medium pump speed (GP1)",
            "silver_parameter_name": "heat_circuit_pump_speed",
            "value_mappings": {},
        },
        43439: {
            "bronze_parameter_name": "Brine pump speed (GP1)",
            "silver_parameter_name": "brine_circuit_pump_speed",
            "value_mappings": {},
        },
        49994: {
            "bronze_parameter_name": "Priority",
            "silver_parameter_name": "priority",
            "value_mappings": {
                10: "off",
                20: "hot_water",
                30: "heating",
                60: "cooling",
            },
        },
    }
