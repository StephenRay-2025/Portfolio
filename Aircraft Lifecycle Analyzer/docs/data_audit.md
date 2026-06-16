# Data Audit

## Aircraft Dataset (aircraft.parquet)
- **Row count**: 501
- **Column count**: 25
- **Field names**: id, shortname, manufacturer, name, type, priority, eid, ename, speed, fuel, co2, cost, capacity, rwy, check_cost, range, ceil, maint, pilots, crew, engineers, technicians, img, wingspan, length
- **Missing values**: {'id': 0, 'shortname': 0, 'manufacturer': 0, 'name': 0, 'type': 0, 'priority': 0, 'eid': 0, 'ename': 0, 'speed': 0, 'fuel': 0, 'co2': 0, 'cost': 0, 'capacity': 0, 'rwy': 0, 'check_cost': 0, 'range': 0, 'ceil': 0, 'maint': 0, 'pilots': 0, 'crew': 0, 'engineers': 0, 'technicians': 0, 'img': 0, 'wingspan': 0, 'length': 0}
- **Sample record**: {'id': 1, 'shortname': 'b744', 'manufacturer': 'Boeing', 'name': 'B747-400', 'type': 0, 'priority': 0, 'eid': 4, 'ename': 'PW4056', 'speed': 982.2999877929688, 'fuel': 22.889999389648438, 'co2': 0.18000000715255737, 'cost': 92136845, 'capacity': 416, 'rwy': 10250, 'check_cost': 7140605, 'range': 14500, 'ceil': 40000, 'maint': 330, 'pilots': 2, 'crew': 13, 'engineers': 4, 'technicians': 4, 'img': 'assets/img/aircraft/png/747-8.png', 'wingspan': 64, 'length': 70}

## Airports Dataset (airports.parquet)
- **Row count**: 3907
- **Column count**: 13
- **Field names**: id, name, fullname, country, continent, iata, icao, lat, lng, rwy, market, hub_cost, rwy_codes
- **Missing values**: {'id': 0, 'name': 0, 'fullname': 0, 'country': 0, 'continent': 0, 'iata': 0, 'icao': 0, 'lat': 0, 'lng': 0, 'rwy': 0, 'market': 0, 'hub_cost': 0, 'rwy_codes': 0}
- **Sample record**: {'id': 1, 'name': 'Honiara', 'fullname': 'Honiara International Airport', 'country': 'Solomon Islands', 'continent': 'Oceania', 'iata': 'HIR', 'icao': 'AGGH', 'lat': -9.4280004501343, 'lng': 160.05499267578, 'rwy': 7218, 'market': 55, 'hub_cost': 213300, 'rwy_codes': '06/24'}
- **Countries represented**: 232 (e.g., Solomon Islands, Nauru, Papua New Guinea, Greenland, Iceland...)

## Route Dataset (route.parquet)
- **Row count**: 7630371
- **Column count**: 4
- **Field names**: yd, jd, fd, d
- **Missing values**: {'yd': 0, 'jd': 0, 'fd': 0, 'd': 0}
- **Sample record**: {'yd': 542, 'jd': 182, 'fd': 45, 'd': 330.21963764776416}
- **Field 'd' statistics**: min=2.38, max=20009.28, mean=8602.27
- **Note on 'd'**: Need to examine relation with aircraft (yd), origin (jd), destination (fd) to infer meaning.

## Routes Dataset (routes.parquet) (if exists)
- **Row count**: 7630371
- **Column count**: 4
- **Field names**: yd, jd, fd, d
- **Missing values**: {'yd': 0, 'jd': 0, 'fd': 0, 'd': 0}
- **Sample record**: {'yd': 542, 'jd': 182, 'fd': 45, 'd': 330.21963764776416}

