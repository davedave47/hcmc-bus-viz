# 05 — Schema Map

*Cross-table column overlap + computed joinability. Inferred purely from column names + value overlap; no business rules applied.*

## Shared column names (candidate join keys)

| column | tables (count) | tables (list) |
|---|---:|---|
| `route_id` | 7 | `afc.route_stops`, `afc.routes`, `afc.trips`, `gps.routes`, `gps.schedules`, `gps.trips`, `root.vehicle_route_mapping` |
| `lng` | 5 | `afc.stations`, `afc.tickets`, `gps.raw_pings`, `gps.stations`, `root.hcmc_stops_agu_2025` |
| `lat` | 5 | `afc.stations`, `afc.tickets`, `gps.raw_pings`, `gps.stations`, `root.hcmc_stops_agu_2025` |
| `direction` | 5 | `afc.route_stops`, `afc.trips`, `gps.extracted_trips`, `gps.schedules`, `gps.trips` |
| `station_id` | 5 | `afc.route_stops`, `afc.stations`, `afc.tickets`, `gps.stations`, `gps.stop_times` |
| `trip_id` | 5 | `afc.tickets`, `afc.trips`, `gps.extracted_trips`, `gps.stop_times`, `gps.trips` |
| `company_id` | 4 | `afc.companies`, `afc.routes`, `gps.companies`, `gps.routes` |
| `type` | 3 | `gps.routes`, `gps.stations`, `root.hcmc_stops_agu_2025` |
| `vehicle` | 3 | `gps.extracted_trips`, `gps.raw_pings`, `root.vehicle_route_mapping` |
| `route_no` | 3 | `afc.routes`, `gps.routes`, `root.vehicle_route_mapping` |
| `driver_license_number` | 3 | `afc.drivers`, `afc.trips`, `gps.drivers` |
| `date` | 3 | `gps.extracted_trips`, `gps.raw_pings`, `gps.trips` |
| `code` | 2 | `gps.stations`, `root.hcmc_stops_agu_2025` |
| `zone` | 2 | `gps.stations`, `root.hcmc_stops_agu_2025` |
| `address` | 2 | `gps.stations`, `root.hcmc_stops_agu_2025` |
| `status` | 2 | `gps.stations`, `root.hcmc_stops_agu_2025` |
| `company_name` | 2 | `afc.companies`, `gps.companies` |
| `driver_id` | 2 | `gps.drivers`, `gps.trips` |
| `driver_name` | 2 | `afc.drivers`, `gps.drivers` |
| `route_id_mcpt` | 2 | `gps.routes`, `gps.schedules` |
| `route_name` | 2 | `afc.routes`, `gps.routes` |
| `departure_time` | 2 | `gps.schedules`, `gps.stop_times` |
| `arrival_time` | 2 | `gps.schedules`, `gps.stop_times` |
| `station_name` | 2 | `afc.stations`, `gps.stations` |
| `vehicle_id` | 2 | `gps.trips`, `gps.vehicles` |
| `vehicle_number` | 2 | `afc.buses`, `gps.vehicles` |
| `driver` | 2 | `gps.extracted_trips`, `gps.raw_pings` |
| `bus_id` | 2 | `afc.buses`, `afc.trips` |
| `school_id` | 2 | `afc.schools`, `afc.students` |
| `student_id` | 2 | `afc.students`, `afc.users` |
| `user_id` | 2 | `afc.tickets`, `afc.users` |
| `ticket_id` | 2 | `afc.payments`, `afc.tickets` |

## Computed joinability (directional overlap %)

| col | A | B | A unique | B unique | shared | A in B % | B in A % | interpretation |
|---|---|---|---:|---:|---:|---:|---:|---|
| `ticket_id` | `afc.tickets` | `afc.payments` | 585,208 | 585,208 | 585,208 | 100.0 | 100.0 | **full overlap** — safe join |
| `lat` | `gps.raw_pings` | `afc.tickets` | 154,507 | 126,186 | 78,355 | 50.71 | 62.09 | partial — populations differ |
| `trip_id` | `afc.trips` | `afc.tickets` | 1,199,766 | 36,737 | 36,737 | 3.06 | 100.0 | high one-way overlap — child→parent join |
| `lng` | `gps.raw_pings` | `afc.tickets` | 36,302 | 38,417 | 10,533 | 29.01 | 27.42 | **lossy** — likely different keyspaces |
| `station_id` | `afc.route_stops` | `afc.stations` | 5,502 | 5,502 | 5,502 | 100.0 | 100.0 | **full overlap** — safe join |
| `code` | `root.hcmc_stops_agu_2025` | `gps.stations` | 4,706 | 4,706 | 4,706 | 100.0 | 100.0 | **full overlap** — safe join |
| `station_id` | `gps.stations` | `afc.route_stops` | 4,710 | 5,502 | 4,660 | 98.94 | 84.7 | high one-way overlap — child→parent join |
| `station_id` | `gps.stations` | `afc.stations` | 4,710 | 5,502 | 4,660 | 98.94 | 84.7 | high one-way overlap — child→parent join |
| `lng` | `root.hcmc_stops_agu_2025` | `gps.stations` | 4,564 | 4,564 | 4,564 | 100.0 | 100.0 | **full overlap** — safe join |
| `lat` | `root.hcmc_stops_agu_2025` | `gps.stations` | 4,558 | 4,558 | 4,558 | 100.0 | 100.0 | **full overlap** — safe join |
| `lng` | `root.hcmc_stops_agu_2025` | `afc.stations` | 4,564 | 5,289 | 4,494 | 98.47 | 84.97 | high one-way overlap — child→parent join |
| `lng` | `gps.stations` | `afc.stations` | 4,564 | 5,289 | 4,494 | 98.47 | 84.97 | high one-way overlap — child→parent join |
| `lat` | `root.hcmc_stops_agu_2025` | `afc.stations` | 4,558 | 5,296 | 4,483 | 98.35 | 84.65 | high one-way overlap — child→parent join |
| `lat` | `gps.stations` | `afc.stations` | 4,558 | 5,296 | 4,483 | 98.35 | 84.65 | high one-way overlap — child→parent join |
| `address` | `root.hcmc_stops_agu_2025` | `gps.stations` | 3,748 | 3,748 | 3,748 | 100.0 | 100.0 | **full overlap** — safe join |
| `station_id` | `afc.route_stops` | `afc.tickets` | 5,502 | 4,587 | 3,437 | 62.47 | 74.93 | partial — populations differ |
| `station_id` | `afc.stations` | `afc.tickets` | 5,502 | 4,587 | 3,437 | 62.47 | 74.93 | partial — populations differ |
| `station_id` | `gps.stations` | `afc.tickets` | 4,710 | 4,587 | 3,415 | 72.51 | 74.45 | partial — populations differ |
| `lat` | `gps.raw_pings` | `afc.stations` | 154,507 | 5,296 | 2,959 | 1.92 | 55.87 | partial — populations differ |
| `station_name` | `gps.stations` | `afc.stations` | 2,909 | 3,431 | 2,860 | 98.32 | 83.36 | high one-way overlap — child→parent join |
| `lat` | `root.hcmc_stops_agu_2025` | `gps.raw_pings` | 4,558 | 154,507 | 2,849 | 62.51 | 1.84 | partial — populations differ |
| `lat` | `gps.stations` | `gps.raw_pings` | 4,558 | 154,507 | 2,849 | 62.51 | 1.84 | partial — populations differ |
| `lat` | `afc.stations` | `afc.tickets` | 5,296 | 126,186 | 2,657 | 50.17 | 2.11 | partial — populations differ |
| `lat` | `root.hcmc_stops_agu_2025` | `afc.tickets` | 4,558 | 126,186 | 2,550 | 55.95 | 2.02 | partial — populations differ |
| `lat` | `gps.stations` | `afc.tickets` | 4,558 | 126,186 | 2,550 | 55.95 | 2.02 | partial — populations differ |
| `bus_id` | `afc.buses` | `afc.trips` | 2,362 | 2,362 | 2,362 | 100.0 | 100.0 | **full overlap** — safe join |
| `trip_id` | `gps.stop_times` | `gps.trips` | 1,244 | 1,244 | 1,244 | 100.0 | 100.0 | **full overlap** — safe join |
| `lng` | `gps.raw_pings` | `afc.stations` | 36,302 | 5,289 | 1,183 | 3.26 | 22.37 | **lossy** — likely different keyspaces |
| `lng` | `root.hcmc_stops_agu_2025` | `gps.raw_pings` | 4,564 | 36,302 | 1,123 | 24.61 | 3.09 | **lossy** — likely different keyspaces |
| `lng` | `gps.stations` | `gps.raw_pings` | 4,564 | 36,302 | 1,123 | 24.61 | 3.09 | **lossy** — likely different keyspaces |
| `student_id` | `afc.students` | `afc.users` | 1,048 | 950 | 950 | 90.65 | 100.0 | high one-way overlap — child→parent join |
| `lng` | `afc.stations` | `afc.tickets` | 5,289 | 38,417 | 819 | 15.48 | 2.13 | **lossy** — likely different keyspaces |
| `vehicle_number` | `gps.vehicles` | `afc.buses` | 2,550 | 2,069 | 757 | 29.69 | 36.59 | partial — populations differ |
| `lng` | `root.hcmc_stops_agu_2025` | `afc.tickets` | 4,564 | 38,417 | 715 | 15.67 | 1.86 | **lossy** — likely different keyspaces |
| `lng` | `gps.stations` | `afc.tickets` | 4,564 | 38,417 | 715 | 15.67 | 1.86 | **lossy** — likely different keyspaces |
| `station_id` | `gps.stations` | `gps.stop_times` | 4,710 | 701 | 701 | 14.88 | 100.0 | high one-way overlap — child→parent join |
| `station_id` | `gps.stop_times` | `afc.route_stops` | 701 | 5,502 | 698 | 99.57 | 12.69 | high one-way overlap — child→parent join |
| `station_id` | `gps.stop_times` | `afc.stations` | 701 | 5,502 | 698 | 99.57 | 12.69 | high one-way overlap — child→parent join |
| `driver_license_number` | `afc.drivers` | `afc.trips` | 660 | 660 | 660 | 100.0 | 100.0 | **full overlap** — safe join |
| `station_id` | `gps.stop_times` | `afc.tickets` | 701 | 4,587 | 532 | 75.89 | 11.6 | partial — populations differ |
| `user_id` | `afc.users` | `afc.tickets` | 948 | 368 | 306 | 32.28 | 83.15 | high one-way overlap — child→parent join |
| `route_id` | `afc.routes` | `afc.trips` | 131 | 146 | 131 | 100.0 | 89.73 | high one-way overlap — child→parent join |
| `driver_id` | `gps.drivers` | `gps.trips` | 1,764 | 124 | 124 | 7.03 | 100.0 | high one-way overlap — child→parent join |
| `vehicle_id` | `gps.trips` | `gps.vehicles` | 123 | 2,550 | 123 | 100.0 | 4.82 | high one-way overlap — child→parent join |
| `route_no` | `gps.routes` | `afc.routes` | 163 | 128 | 121 | 74.23 | 94.53 | high one-way overlap — child→parent join |
| `route_name` | `gps.routes` | `afc.routes` | 162 | 131 | 111 | 68.52 | 84.73 | high one-way overlap — child→parent join |
| `route_id` | `gps.routes` | `gps.schedules` | 163 | 98 | 98 | 60.12 | 100.0 | high one-way overlap — child→parent join |
| `route_id_mcpt` | `gps.routes` | `gps.schedules` | 163 | 99 | 98 | 60.12 | 98.99 | high one-way overlap — child→parent join |
| `route_id` | `afc.route_stops` | `afc.trips` | 193 | 146 | 67 | 34.72 | 45.89 | partial — populations differ |
| `school_id` | `afc.schools` | `afc.students` | 60 | 60 | 60 | 100.0 | 100.0 | **full overlap** — safe join |
| `route_id` | `afc.route_stops` | `afc.routes` | 193 | 131 | 59 | 30.57 | 45.04 | partial — populations differ |
| `driver_license_number` | `gps.drivers` | `afc.drivers` | 1,763 | 660 | 42 | 2.38 | 6.36 | **lossy** — likely different keyspaces |
| `driver_license_number` | `gps.drivers` | `afc.trips` | 1,763 | 660 | 42 | 2.38 | 6.36 | **lossy** — likely different keyspaces |
| `route_id` | `root.vehicle_route_mapping` | `afc.route_stops` | 31 | 193 | 31 | 100.0 | 16.06 | high one-way overlap — child→parent join |
| `route_no` | `root.vehicle_route_mapping` | `afc.routes` | 33 | 128 | 30 | 90.91 | 23.44 | high one-way overlap — child→parent join |
| `trip_id` | `gps.stop_times` | `gps.extracted_trips` | 1,244 | 30 | 30 | 2.41 | 100.0 | high one-way overlap — child→parent join |
| `trip_id` | `gps.trips` | `gps.extracted_trips` | 1,244 | 30 | 30 | 2.41 | 100.0 | high one-way overlap — child→parent join |
| `route_no` | `root.vehicle_route_mapping` | `gps.routes` | 33 | 163 | 29 | 87.88 | 17.79 | high one-way overlap — child→parent join |
| `zone` | `root.hcmc_stops_agu_2025` | `gps.stations` | 28 | 28 | 28 | 100.0 | 100.0 | **full overlap** — safe join |
| `company_id` | `gps.companies` | `afc.companies` | 10 | 10 | 10 | 100.0 | 100.0 | **full overlap** — safe join |
| `company_id` | `gps.companies` | `afc.routes` | 10 | 10 | 10 | 100.0 | 100.0 | **full overlap** — safe join |
| `company_id` | `afc.companies` | `afc.routes` | 10 | 10 | 10 | 100.0 | 100.0 | **full overlap** — safe join |
| `company_name` | `gps.companies` | `afc.companies` | 10 | 10 | 10 | 100.0 | 100.0 | **full overlap** — safe join |
| `type` | `root.hcmc_stops_agu_2025` | `gps.stations` | 9 | 9 | 9 | 100.0 | 100.0 | **full overlap** — safe join |
| `route_id` | `root.vehicle_route_mapping` | `afc.trips` | 31 | 146 | 9 | 29.03 | 6.16 | **lossy** — likely different keyspaces |
| `route_id` | `gps.routes` | `gps.trips` | 163 | 9 | 9 | 5.52 | 100.0 | high one-way overlap — child→parent join |
| `route_id` | `gps.schedules` | `gps.trips` | 98 | 9 | 9 | 9.18 | 100.0 | high one-way overlap — child→parent join |
| `company_id` | `gps.companies` | `gps.routes` | 10 | 9 | 9 | 90.0 | 100.0 | high one-way overlap — child→parent join |
| `company_id` | `gps.routes` | `afc.companies` | 9 | 10 | 9 | 100.0 | 90.0 | high one-way overlap — child→parent join |
| `company_id` | `gps.routes` | `afc.routes` | 9 | 10 | 9 | 100.0 | 90.0 | high one-way overlap — child→parent join |
| `route_id` | `root.vehicle_route_mapping` | `afc.routes` | 31 | 131 | 8 | 25.81 | 6.11 | **lossy** — likely different keyspaces |
| `status` | `root.hcmc_stops_agu_2025` | `gps.stations` | 5 | 5 | 5 | 100.0 | 100.0 | **full overlap** — safe join |
| `driver` | `gps.raw_pings` | `gps.extracted_trips` | 131 | 5 | 5 | 3.82 | 100.0 | high one-way overlap — child→parent join |
| `vehicle` | `gps.raw_pings` | `gps.extracted_trips` | 131 | 4 | 4 | 3.05 | 100.0 | high one-way overlap — child→parent join |
| `direction` | `gps.schedules` | `gps.trips` | 2 | 2 | 2 | 100.0 | 100.0 | **full overlap** — safe join |
| `direction` | `gps.schedules` | `gps.extracted_trips` | 2 | 2 | 2 | 100.0 | 100.0 | **full overlap** — safe join |
| `direction` | `gps.schedules` | `afc.route_stops` | 2 | 2 | 2 | 100.0 | 100.0 | **full overlap** — safe join |
| `direction` | `gps.trips` | `gps.extracted_trips` | 2 | 2 | 2 | 100.0 | 100.0 | **full overlap** — safe join |
| `direction` | `gps.trips` | `afc.route_stops` | 2 | 2 | 2 | 100.0 | 100.0 | **full overlap** — safe join |
| `direction` | `gps.extracted_trips` | `afc.route_stops` | 2 | 2 | 2 | 100.0 | 100.0 | **full overlap** — safe join |
| `date` | `gps.trips` | `gps.raw_pings` | 1 | 1 | 1 | 100.0 | 100.0 | **full overlap** — safe join |
| `date` | `gps.trips` | `gps.extracted_trips` | 1 | 1 | 1 | 100.0 | 100.0 | **full overlap** — safe join |
| `date` | `gps.raw_pings` | `gps.extracted_trips` | 1 | 1 | 1 | 100.0 | 100.0 | **full overlap** — safe join |

## Per-table PK candidates

| table | PK candidate(s) |
|---|---|
| `afc.buses` | _(none — no unique 0-null column)_ |
| `afc.companies` | `company_id`, `company_name` |
| `afc.drivers` | _(none — no unique 0-null column)_ |
| `afc.payments` | `ticket_id` |
| `afc.route_stops` | _(none — no unique 0-null column)_ |
| `afc.routes` | _(none — no unique 0-null column)_ |
| `afc.schools` | `school_id`, `school_name`, `school_address` |
| `afc.stations` | `station_id` |
| `afc.students` | _(none — no unique 0-null column)_ |
| `afc.tickets` | `ticket_id`, `ticket_uuid` |
| `afc.trips` | _(none — no unique 0-null column)_ |
| `afc.users` | _(none — no unique 0-null column)_ |
| `gps.companies` | `company_id`, `company_name` |
| `gps.drivers` | `driver_id` |
| `gps.extracted_trips` | _(none — no unique 0-null column)_ |
| `gps.raw_pings` | _(none — no unique 0-null column)_ |
| `gps.routes` | _(none — no unique 0-null column)_ |
| `gps.schedules` | _(none — no unique 0-null column)_ |
| `gps.stations` | `station_id` |
| `gps.stop_times` | _(none — no unique 0-null column)_ |
| `gps.trips` | `trip_id` |
| `gps.vehicles` | `vehicle_id`, `vehicle_number` |
| `root.hcmc_stops_agu_2025` | `stopId` |
| `root.vehicle_route_mapping` | _(none — no unique 0-null column)_ |