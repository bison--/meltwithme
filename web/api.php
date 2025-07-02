<?php

try {
    require_once "conf_local.php";
} catch (Exception $ex) {
    require_once "conf.php";
}

class API {
    function doRequest($query)
    {
        $data = json_decode(file_get_contents("data.json"));
        if ($query == "temperature") {
            return $data->temperature . " °C";
        }

        if ($query == "co2") {
            return "CO2 " . $data->co2 . " ppm";
        }

        if ($query == "date") {
            return $data->date;
        }

        return "";
    }

    function pushData($key, $payload)
    {
        if ($key != API_KEY) {
            return;
        }

        file_put_contents("data.json", $payload);
    }
}

$api = new API();

if (isset($_REQUEST['request'])) {
    /*
     * ?request=temperature
     * ?request=co2
     * ?request=date
     */

    print $api->doRequest($_REQUEST['request']);
} elseif (isset($_REQUEST['push'])) {
    // ?push=KEY&payload=json

    //file_put_contents("data.txt", print_r($_REQUEST['payload'], true));
    $api->pushData($_REQUEST['push'], $_REQUEST['payload']);
    //print_r($_REQUEST);
} else {
    //print 'ELSE: ';
    //print_r($_REQUEST);
}



