_**sustainability**_ 

## _Article_ 

## **GPS Data Analytics for the Assessment of Public City Bus Transportation Service Quality in Bangkok** 

**Rathachai Chawuthai[1] , Agachai Sumalee[2] and Thanunchai Threepak[1,] *** 

- 1 School of Engineering, King Mongkut’s Institute of Technology Ladkrabang, Bangkok 10520, Thailand; rathachai.ch@kmitl.ac.th 

- 2 School of Integrated Innovation, Chulalongkorn University, Bangkok 10330, Thailand; agachai.s@chula.ac.th ***** Correspondence: thanunchai.th@kmitl.ac.th; Tel.: +66-2329-8341 (ext. 114) 

**Abstract:** Evaluation of the quality of service (QoS) of public city buses is generally performed using surveys that assess attributes such as accessibility, availability, comfort, convenience, reliabilities, safety, security, etc. Each survey attribute is assessed from the subjective viewpoint of the service users. This is reliable and straightforward because the consumer is the one who accesses the bus service. However, in addition to summarizing personal feedback from humans, using data analytics has become another useful method for assessing the QoS of bus transportation. This work aims to use global positioning system (GPS) data to measure the reliability, accessibility, and availability of bus transportation services. There are three QoS scoring functions for tracking complete trips, on-path driving, and on-schedule operation. In the analytical process, GPS coordinates rounding is adopted and applied for detecting trips on each route path. After assessing the three QoS scores, it has been found that most bus routes have good operations with high scores, while some bus routes show room for improvement. Future work could use our data to create recommendations for policy makers in terms of how to improve a city’s smart mobility. 

**Keywords:** bus transportation; GPS data analytics; quality of service; smart city; smart mobility; urban informatics 

## **1. Introduction** 

**Citation:** Chawuthai, R.; Sumalee, A.; Threepak, T. GPS Data Analytics for the Assessment of Public City Bus Transportation Service Quality in Bangkok. _Sustainability_ **2023** , _15_ , 5618. https://doi.org/10.3390/su15075618 

Academic Editor: Juneyoung Park 

Received: 30 January 2023 Revised: 18 March 2023 Accepted: 20 March 2023 Published: 23 March 2023 

**Copyright:** © 2023 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https:// creativecommons.org/licenses/by/ 4.0/). 

City bus transportation is a public transportation option that is commonly used in many countries as it supports the growing transportation demand and takes into account affordability for passengers [1]. Thus, having qualified bus services becomes a key factor for smart life in a city. In this case, before enhancing the service quality, we need to understand the current quality of service (QoS) of bus transportation, then improve it point by point. The QoS of city bus transportation is generally measured by user surveys: e.g., Wethyavivorn and Sukwattanakorn [2], Ueasangkomsate [3], Chan et al. [4], Page and Yue [5], and Goyal et al. [6]. These studies found that the common issues are accessibility, availability, reliability, security, and comfortability. As to research from Thailand, the authors of [2,3] stated that passengers in particular areas of Bangkok had serious concerns about the physical facilities and service reliability. The results of [3] were reported to the government to help it plan policies for enhancing the efficiency of public buses. The relevant works are reviewed in Section 2 and summarized in Table 1. 

As can be seen, survey results help a city to explore issues from the viewpoints of users in order to improve bus services. It is well known that survey results depend on the individual. This means that obtaining feedback from a large number of people can reflect most of the problems and needs of citizens. However, in the age of data technology, using data to measure the quality of service of city bus transportation has become another way to understand the issues. Thus, this work aims to contribute data for measuring the QoS of bus transportation by focusing on the aspects of accessibility, availability, and reliability, which can benefit directly from data analytics. 

_Sustainability_ **2023** , _15_ , 5618. https://doi.org/10.3390/su15075618 

https://www.mdpi.com/journal/sustainability 

_Sustainability_ **2023** , _15_ , 5618 

2 of 23 

To conduct data analytics in the transportation domain, global positioning system (GPS) data are the key to exploring useful results, e.g., travel time variability analytics [7], GPS data processing methods [8], the transfer time and waiting time of bus passengers [9], rural–urban migrant analytics during the COVID-19 pandemic [10], traffic monitoring [11], predictive transportation [12,13], road defect monitoring [14], etc. Thanks to a joint project between King Mongkut’s Institute of Technology Ladkrabang and the Department of Land Transport of Thailand, global positioning system (GPS) data from buses and city data from Bangkok have been beneficial to our research study. This work aims to use GPS data analytics and spatial data analytics to improve the quality of bus transportation in Bangkok, Thailand. As there are several previous works using buses’ GPS data to examine aspects such as travel time, transfer time, waiting time, and number of transfers [7,9], this work focuses on other issues under the criteria of reliability, accessibility, and availability. First, in terms of reliability, we assess whether every bus route provides the number of completed trips promised. Second, to gauge accessibility, we assess whether every driving route covers the whole route path. Last, to demonstrate the availability, we assess the frequency of every bus sticking to its timetable. In this way, we aim to measure the quality of services (QoS) of bus transportation by the following objectives: 

1. To track complete bus trips based on commitments. 

2. To track on-path driving following operated routes. 

3. To track on-schedule operation according to schedule conditions. 

**Table 1.** Summary of literature studies on the uses of GPS technology for transportation and the quality of service of bus transportation. 

|**Reference**|**Year**|**Summary**|**Lesson Learned**|
|---|---|---|---|
|||Reviewed the uses of the GPS technology of|Survey purposes, samples, and techniques|
|Shen and Stopher [8]|2014|mobile phones and applications for travel|of each work; details of five steps for GPS|
|||survey from many works.|data processing.|
|Mazloumi<br>et al. [7]|2010|Used GPS data to analyze travel time<br>variability against other<br>traffic-related factors.|Some significant factors, such as segment<br>length, off-peak time, etc., contributing to<br>the travel time variability.|
|Gschwendar<br>et al. [9]|2016|Used data from smart cards and GPS for<br>analyzing the uses of buses.|The results of travel time, transfer time,<br>number of transfers, and waiting time are<br>beneficial for policy makers.|
|Chan et al. [4]|2020|Conducted user surveys before and after<br>installing the GPS system for<br>monitoring buses.|The criteria of accessibility, reliability,<br>comfort, safety, customer satisfaction, and<br>customer loyalty were higher after having<br>the GPS system.|
||||The public transportation matrix, including|
|Page and Yue [5]|2009|Studied the public transportation quality<br>matrix for tourism.|availability, accessibility, information, time,<br>customer care, comfort, security, and|
||||environment, was reviewed.|
|||Proposed multicriteria decision making for|It results in some important criteria, such as|
|Goyal et al. [6]|2022|finding significant criteria for evaluating the|total number of vehicles, scheduled vehicles,|
|||quality of a bus depot.|operated vehicles, off-road vehicles, etc.|
|Wethyavivorn and<br>Sukwattanakorn [2]|2019|Conducted user surveys about travel<br>patterns, modes, and ratings.|There needs to be an improvement in bus<br>frequency, and precise schedules.|
||||Five dimensions, tangibility, reliability,|
|Ueasangkomsate [3]|2019|Conducted user survey about the QoS of<br>public transportations.|responsiveness, assurance, and access, are<br>analyzed; the improvement of some<br>attributes under these dimensions|
||||is required.|



Our approach defines three scoring levels, QoS-1, QoS-2, and QoS-3, to describe all objectives. Taking a closer look at the situation of the management of public city bus transportation in Bangkok, there are four challenges that our work faces. First, there is no wireless sensor detecting a bus at a bus stop; as some works have mentioned [15,16], 

_Sustainability_ **2023** , _15_ , 5618 

3 of 23 

the analytics of GPS transactions with route polylines are adopted to detect trips of buses. Second, a bus route in Bangkok could take several different courses depending on the demand from passengers and the strategies of the bus operators. There must be main routes on a bus route, but it is also possible to have subpaths, which are shorter versions of the main path, and split paths, which diverge from the main path to go to other destinations. Third, a bus can choose any paths in a day following the schedule conditions from a bus route provider, so we need to use data analytics to detect the path that a bus drove through. Last, there is no executable timetable to show the departure time. In fact, schedule conditions only provide the number of trips in any time period, while bus providers manage the departure time by themselves. 

Due to these issues, data analytics on GPS data and other datasets is mainly employed to determine the QoS scores. In this case, our method provides four phases, input, preprocessing, scoring, and output, as depicted in Figure 1. Input data are the GPS transaction of buses, the polyline of every bus route, and the schedule conditions of all bus routes. To work with GPS data, the techniques of GPS coordinates rounding is adopted at the preprocessing phase. Then, bus trips and metadata are calculated in order to measure three QoS scoring functions. Our work resulted in the QoS score of each bus route for the three months of the last quarter of 2021, and found that there was room for improvement in the sustainability of bus transportation services. 

input pre-processing scoring output TrajectoryComplete Bus GPS Route Bus-Trip Bus Trips QoS-1 Score Transactions Detecting _(3.2.1)_ Matching _(3.3.2) (3.4.1)_ Tracking _(3.5)_ Path Bus Driving Bus Route On-Path Bounding Box Route QoS-2 Score polylines Detecting Calculating Tracking _(3.2.2) (3.4.2) (3.3.1) (3.6)_ Bus Bus Schedule QoS-3 Score Schedule Conditions oe ~~s~~ Tracking _(3.2.3) (3.7)_ **Figure 1.** Our overall approach. The details of each module are described by the number of subsections in parentheses. 

This manuscript contains five sections. The first provides an overall introduction to our work. Second, we review the uses of GPS in transportation, the quality of service of bus transportation, and the technical methods of GPS data processing. The third section explains about the data and proposed methods for calculating the three QoS scoring functions. The fourth section demonstrates the results of our analytical methods in the form of tables and charts, together with a discussion. In the last section, a summary and recommended future work based on our approach are provided. 

## **2. Literature Review** 

This section studies the uses of GPS technology for transportation and the QoS of bus transportation in several works, which are summarized in Table 1. In addition, the technique of GPS coordinates, which is used to analyze spatial data, is reviewed. 

_Sustainability_ **2023** , _15_ , 5618 

4 of 23 

## _2.1. The Uses of GPS Technology for Transportation_ 

GPS technology has been used in the transportation domain for decades [8]. Shen and Stopher [8] found that there were many attempts to use GPS technology in addition to traditional survey methods, for example, to monitor travel behavior changes, route choice, residential selection, etc. Based on the coordinates data gathered from smartphones and GPS devices, they analyzed spatial data to assess trips, travel time, activities, etc. This work also summarized the processing steps of GPS data: preprocessing, trip identification, mode detection, purpose imputation, and analytical results. GPS data analytics can give insight into public transportation, as studied by Mazloumi et al. [7]. This work used GPS transactions from buses in Melbourne, Australia to determine the travel time variability. The standard deviation of travel time was explored with a period of four hours per day. Since a high value leads to poor performance in transportation, they found that the factors of section length (km), number of signalized intersections per km, and number of stops per km contributed to the increase in this value; while off-peak time and industrial area provided a lower value. This result can assist bus operators with planning their bus schedules so that the arrival time corresponds to the actual situation. In addition, working with other data helps to gather more useful results—for example, Gschwendar et al. using smart card and GPS data [9]. The analytics of using smart cards as payment for bus services resulted in data on travel time, transfer time, number of transfers, and waiting time as well as the passenger demands. Based on the analytical results of these indicators under the dimensions of time and space, the public transport authority and bus operators could work together to improve policies and transportation plans to truly meet the needs of users. 

## _2.2. Quality of Service of Bus Transportation_ 

As urban bus services are readily available as an affordable, accessible, and sustainable mode of transportation, they are crucial to the movement of people inside cities [1]. However, the QoS of urban bus systems is often inadequate, which can negatively impact ridership and lead to a decline in the overall performance of the system. There has been research devoted to the QoS of public transportation, especially bus transportation. 

Chan et al. [4] used real-time GPS tracking to improve the quality of bus services. Their work implemented an application for collecting passengers’ feedback via surveys before and after installing a real-time GPS tracking system. There were six criteria for assessing the quality of service: accessibility, reliability, comfort, safety, customer satisfaction, and customer loyalty. The results showed that all scores after GPS tracking were significantly higher than before having it. This work also noted that when passengers knew the bus schedule and actual situation, they were willing to preplan their trip, and were pleased with the safe and comfortable transit. Thus, this work demonstrated the feasibility of using GPS tracking for enhancing the quality of service, although it did not use GPS data analytics to measure the QoS. 

To measure the public transportation quality, a tourism matrix was studied in [5]. There were eight factors considered: availability, accessibility, information, time, customer care, comfort, security, and environment. The travel modes, such as coach and bus transportation, cycling, rail travel, cruising, ferries, air transportation, etc. were studied in order to highlight points of policy and planning issues. All of these aspects can be evaluated using user surveys; however, to be data-driven as part of smart mobility, some of them such as availability, accessibility, and time can take advantage of GPS data. 

Goyal et al. [6] provided summary statistics of bus quality in Rajasthan State during 2018 and 2019. The major categories are operational service, passenger service, cost effects, and quality. This work introduced multicriteria decision making for assisting decision makers with selecting significant criteria for assessing the performance of a bus depot. The criteria of the operational service are feasible to evaluate by GPS data. These are the total number of vehicles, number of scheduled vehicles, number of operating vehicles, number of off-road vehicles, number of scheduled trips, number of operating trips, number of 

_Sustainability_ **2023** , _15_ , 5618 

5 of 23 

extra trips, number of curtailed trips, total number of employees, number of routes, and route distance. 

Other works from Thailand [2,3] surveyed the QoS of public transportation based on five dimensions: tangibility, reliability, responsiveness, assurance, and access. The authors analyzed the results and concluded that the perceived quality of service in the Bangkok metropolitan area and the East region was similarly poor and improvement is required on some attributes, such as the number of buses, availability, precise bus schedules, buses’ current locations, safety, driver ability, interconnection of the transport system, etc. 

## _2.3. GPS Coordinates Rounding_ 

GPS coordinates are used to precisely identify the location of a point on the Earth’s surface. However, in some cases, it may be necessary to round the coordinates of a GPS location to the nearest whole number, in order to obscure the exact location or protect the privacy of individuals. This process is known as GPS coordinates rounding [17–20]. One approach to GPS coordinates rounding is to use a “rounding box.” A rounding box is a geographic area within which the GPS coordinates of a location will be rounded to the same whole number [17]. For example, a rounding box of size 2 would round the GPS coordinates of all locations within the box to be the same location, digits of the coordinate (13.34213, 100.42345) being (13.34, 100.42). Several works have employed the technique of GPS coordinates rounding. Huang et al. [17] used rounding boxes of a route to find the intersecting parts of two routes. Elevelt et al. [18] used locations from surveys to summary citizens’ activities by areas in the Netherlands, and also applied three-digit rounding boxes that bound spatial precision areas to about 100 m. Ciociola et al. [19] employed rounding boxes at three decimals of GPS location for analyzing trips made by electronic scooters in the USA. Payyanadan et al. [20] introduced a method to measure the risks of routes for older drivers. This research used different rounding decimals, four-digit rounded latitudes and three-digit rounded longitudes, due to the curvature degree of the earth at the focus area. 

## **3. Materials and Methods** 

As seen from the review in Section 2 and the summary in Table 1, there is a high possibility of using GPS data to measure the QoS of city bus transportation. Some aspects, such as travel time, transfer time, number of transfers, waiting time, road conditions, and time periods, were analyzed by GPS technology [7–9]. In addition, many criteria, such as accessibility, availability, reliability, comfort, safety, customer satisfaction, customer loyalty, bus frequency, precise schedules, responsiveness, assurance, etc., were evaluated by the survey method [2–6]. Based on previous studies, our work aims to further support the concept of using GPS data for measuring the QoS of city bus transportation. In our work, due to the datasets available and some issues raised in [2,3], the criteria of reliability, accessibility, and availability are underlined in terms of complete trips (QoS-1), on-path driving (QoS-2), and on-schedule operation (QoS-3). 

To achieve our objectives, QoS-1, 2, and 3 were evaluated by step-by-step processing of the input data; our overall work is displayed in Figure 1. There are four main steps: input, preprocessing, scoring, and output. 

First, the input datasets are (1) bus GPS transactions containing bus identifiers, route numbers, coordinates, speeds, and timestamps; (2) bus route polylines, which are sequence sets of coordinates of fixed route paths; and (3) bus schedule containing conditions of each bus route path. Details are given in Section 3.2. 

Second, preprocessing is to process input data in order to prepare clean data for the scoring phase. This involves bounding box calculation and trajectory route matching. The path bounding box calculation creates a polyline of any bus route path into a set of rounding boxes in order to calculate the route matching in the next step. Moreover, trajectory route matching verifies that the location of a bus is along its route path. Further explanation is given in Section 3.3. 

_Sustainability_ **2023** , _15_ , 5618 

6 of 23 

Third, bus trips are analyzed in order to input data for calculating the three QoS scores. The scores are for complete trip tracking, bus-driving route tracking, and bus schedule tracking. This is discussed in Sections 3.4–3.7. 

QoS-1, QoS-2, and QoS-3 scores are the output of the three steps. 

## _3.1. Definitions_ 

Our method introduces various terms, defined as follows: 

- **p** (e.g., p1): An original coordinate point that is a relation comprising of latitude and longitude. 

- **p** _**with a dot**_ (e.g., p1.1): An inner point between original coordinate points. 

- **p*** (e.g., p*1, p*1.1): A rounding box of a coordinate point p. 

- **p*(x,y)** (e.g., p*1(+1,+2)): A neighbor of a p*. For example, if the 2-decimal rounding box p*1 is (13.00, 100.00), the neighbor p*1(+1,+2) is (13.00 + 1 _×_ 0.01, 100.00 + 2 _×_ 0.01) being (13.01, 100.02). 

- **P** (e.g., P1): A path that is a sequence set of p. 

- **P*** (e.g., P1*): A path P whose points are rounded. 

- **P**** (e.g., P1**): A path that contains all neighbors of all coordinate points from P*. 

- - **POR** (b*, P**): A function to detect a point of bus (b*) on a path (P**). 

## _3.2. Data Preparation_ 

There are three main input datasets: (1) GPS transaction data, (2) bus route polylines, and (3) bus schedule conditions. It is noted that some sensitive data such as bus identifiers and route numbers are transformed into alternative labels in order to preserve the privacy of data. 

## 3.2.1. GPS Transaction Data 

A GPS transaction dataset stores GPS data from all buses every minute. There is a GPS box in every bus, and it sends current data to a server. Each entry includes the bid (bus identifier), route (route number), ts (timestamp), lat (latitude), lon (longitude), and speed (speed in km/h). Example data are presented in Table 2. These are GPS transaction entries of a bus with the route number R7234. As we mentioned, the route number is an alias and does not exist in Thailand. 

**Table 2.** Example GPS data of a bus on route R7234. In this table, the bid is a bus identifier, route is a route number, ts is a timestamp, lat is a latitude, lon is a longitude, and speed is a speed in kilometers per an hour. 

|**Bid**|**Route**|**Ts**|**Lat**|**Lon**|**Speed**|
|---|---|---|---|---|---|
|8ead83c5|R7234|2021-10-20 09:39:21|13.729222|100.641610|33|
|8ead83c5|R7234|2021-10-20 09:40:36|13.721500|100.642138|31|
|8ead83c5|R7234|2021-10-20 09:41:36|13.713388|100.643667|63|
|8ead83c5|R7234|2021-10-20 09:42:21|13.709083|100.644722|57|
|8ead83c5|R7234|2021-10-20 09:42:36|13.706860|100.645250|51|
|. . .|. . .|. . .||. . .|. . .|



## 3.2.2. Bus Routes Polylines 

This dataset contains information on the path polylines of each bus route. In Thailand, one route number might have more than one path. These are analyzed into four cases, as depicted in Figure 2. First, as in Figure 2(1), there is one main path with only the go direction. This case is generally a loop transit. Second, as in Figure 2(2), there is a beginning point and an end point having a main path with go and back directions. Third, as in Figure 2(3), there is a subpath from the main path. This is if a bus provider considers shortening a path due to the demand of passengers during rush hour. The end point of this case is still in the main path. Any subpaths must be reported to the government authority. 

_Sustainability_ **2023** , _15_ , 5618 

7 of 23 

Last, as in Figure 2(4), some bus providers have a split path to another end point. For example, when there is a new point of interest such as a new department store, a bus provider considers having a split path to that new place. 

**==> picture [322 x 279] intentionally omitted <==**

**----- Start of picture text -----**<br>
main path / go<br>begin<br>(1)<br>point<br>¡_.———<br>main path / go<br>begin end<br>(2)<br>point point<br>main path / back<br>_——_<br>main path / go<br>begin end<br>(3) point sub path / go main path / back point<br>sub end<br>point<br>eee sub path / back<br>main path / go<br>begin end<br>(4)<br>point split path / go main path / back point<br>split path / back<br>L== TL:<br>split end<br>point<br>a<br>**----- End of picture text -----**<br>


**Figure 2.** Behaviors of bus routes and paths in Thailand. ( **1** ) A loop path. ( **2** ) A two-direction path. ( **3** ) A main path and subpath. ( **4** ) A main path and split path. 

Due to the details of routes and paths described in the previous paragraph, an example of a bus route polylines dataset is presented in Table 3, with route, path_id, path_type, direction, and polyline. Each entry in this table is a single path, where one route can have many paths due to the type and direction of the path. In addition, one route must have a main path with only direction, go or back, but may have many split paths and subpaths. 

- **route** : a route number. 

- **path_id** : a unique identifier of a path. 

- **path_type** : the type of path, that can be main, split, and sub. 

- **direction** : the bus direction of a path, that can be go and back. 

- **begin_point** : the begin point of the polyline. 

- **end_point** : the ending point of the polyline. 

- **polyline** : the sequence set (array) of coordinates. 

**Table 3.** Example of bus route polyline data. 

|**route**|**path_id**|**path_type**|**direction**|**begin_point**|**end_point**|**polyline**|
|---|---|---|---|---|---|---|
|R7234|R7234.00|Main|go|(13.81196, 100.54976)|(13.59013, 100.59738)|[(13.81196, 100.54976),<br>(13.81106, 100.54943),...|
|R7234|R7234.01|Split|go|(13.76977, 100.64184)|(13.60081, 100.74983)|[(13.76977, 100.64184),<br>(13.76865, 100.64196),...|
|R7234|R7234.02|Split|back|(13.60081, 100.74983)|(13.76977, 100.64184)|[(13.60081, 100.74983),<br>(13.60068, 100.74984),...|



_Sustainability_ **2023** , _15_ , 5618 

8 of 23 

**Table 3.** _Cont._ 

|**route**|**path_id**|**path_type**|**direction**|**begin_point**|**end_point**|**polyline**|
|---|---|---|---|---|---|---|
|R7234|R7234.03|Sub|go|(13.76977, 100.64184)|(13.59004, 100.59742)|[(13.76977, 100.64184),<br>(13.76946, 100.64187),...|
|R7234|R7234.04|Sub|back|(13.59004, 100.59742)|(13.76977, 100.64184)|[(13.59004, 100.59742),<br>(13.59013, 100.59738),...|
|R8190|R8190.00|Main|go|(13.74004, 100.49846)|(13.82723, 100.73943)|[(13.74004, 100.49846),<br>(13.74012, 100.49822),...|
|R8190|R8190.01|Main|back|(13.82723, 100.73943)|(13.74004, 100.49846)|[(13.82723, 100.73943),<br>(13.82581, 100.74775),...|
|. . .|. . .|. . .|. . .|. . .|. . .|. . .|



The updated dataset of bus route polyline data from 2021 for Bangkok and its metropolitan area has 1085 entries, including 454 routes, as shown in Figure 3; each route has 2.4 paths, 0.7 split paths, and 0.2 subpaths on average. 

**==> picture [120 x 72] intentionally omitted <==**

**----- Start of picture text -----**<br>
N<br>ASN<br>0 10  km<br>**----- End of picture text -----**<br>


**Figure 3.** City bus route network in Bangkok and metropolitan area. 

## 3.2.3. Bus Schedule Conditions 

The bus schedule conditions dataset is a proposal timetable of each bus route. Every bus provider has to inform the Department of Land Transport about conditions. Since the original documents are paper-based, our work has collected them into a relational database as presented in Table 4. Each entry is the condition of a path, and one path can have many conditions. The fields of this table are in the following list. 

- **con_id** : a condition identifier. 

- **route** : a route number. 

_Sustainability_ **2023** , _15_ , 5618 

9 of 23 

- 

   - **path_id** : a path id. 

- **begin_time** : the beginning time of that condition. 

- **end_time** : the ending time of that condition. 

- **con_type** : a condition type that can be all trips, count, and headway. 

- **param** : a parameter of that condition. 

**Table 4.** Example bus schedule conditions. 

|**con_id**|**route**|**path_id**|**begin_time**|**end_time**|**con_type**|**param**|
|---|---|---|---|---|---|---|
|C0001|R7234|R7234.00|05:00|21:00|all-trips|50|
|C0002|R7234|R7234.00|05:00|21:00|count|50|
|C0003|R7234|R7234.00|06:00|09:00|headway|18|
|C0004|R7234|R7234.00|15:00|18:00|headway|10|
|C0005|R7234|R7234.01|05:00|21:00|all-trips|15|
|C0006|R7234|R7234.01|05:00|21:00|count|15|
|C0007|R7234|R7234.02|05:00|21:00|all-trips|15|
|C0008|R7234|R7234.02|05:00|21:00|count|15|
|C0009|R7234|R7234.03|06:00|10:00|all-trips|60|
|C0010|R7234|R7234.03|06:00|10:00|headway|10|
|C0011|R7234|R7234.04|06:00|10:00|all-trips|60|
|C0012|R7234|R7234.04|06:00|10:00|headway|10|
|C0013|R8190|R8190.00|11:00|18:00|all-trips|10|
|C0014|R8190|R8190.00|11:00|12:00|count|5|
|C0015|R8190|R8190.00|16:00|18:00|headway|30|
|. . .|. . .|. . .|. . .|. . .|. . .|. . .|



The value of the field param is dependent on the con_type. First, each path must have one condition, with con_type being “all trips” in order to check the minimum number of trips. As in the first entry (con_id = 1), the path_id R7234.00 must have 50 trips. Second, if the con_type is “count,” the parameter (param) is the number of buses. If the con_type is “headway,” the parameter is the bus-headway minutes. In this case, the second condition (con_id = C0002) interprets that the number of bus trips on the path “R7234.00” of the route “R7234” between 05:00 and 21:00 must be at least 50. Last, the third condition (con_id = C0003) shows that, between 06:00 and 09:00, the start time of each trip must be no more than 10 min. Conditions C0013, C0014, and C0015 are set to be example cases in the next section. 

## _3.3. Path Rounding Boxes Calculating_ 

To create a map match between GPS data and a path, in general, vector techniques such as the distance from the point to the perpendicular point of the curved surface, and path similarity, provide high performance and high complexity. Several studies, such as [17–20] recommended the rasterization of the vector for working with a large amount of data. Thus, we applied the concepts of rounding boxes from [17] in order to detect bus trips. In this section, GPS coordinates, path rounding boxes, and trajectory route matching are described. 

## 3.3.1. GPS Coordinates and Path Rounding Boxes 

Since GPS coordinates are a floating point number, it consumes processing time to find a nearby location. According to [17], a rounding box of a coordinate can be used as the reference of the same location. For example, the three-digit rounding boxes of (13.65495, 100.22424) and (13.65477, 100.22410) are (13.655, 100.224) and (13.655, 100.224), which are considered as approximately the same location. Thus, a path, which is polylines, can be structured by rounding boxes using the following four steps, together with the demonstration in Figure 4. 

_Sustainability_ **2023** , _15_ , 5618 

10 of 23 

**==> picture [356 x 357] intentionally omitted <==**

**----- Start of picture text -----**<br>
p2 p2<br>p1.2<br>p2.1<br>p1.1<br>p1 p3 p1 p3<br>NN,<br>(1) (2)<br>p2 p2<br>p1.2 p1.2<br>p2.1 p2.1<br>p1.1 p1.1<br>p1 p3 p1 p3<br>aN TOK,<br>(3) (4)<br>p*2 p*(-1,-1) p*(0,-1) p*(1,-1)<br>p*1.2<br>p*1.1 p*(-1,0) p*(0,0) p*(1,0)<br>p*1 OW, p*2.1 p*3<br>p*(-1,1) p*(0,1) p*(1,1)<br>(5) (6)<br>p*2 p*2<br>p*1.2 p*1.2<br>p*1.1 p*1.1<br>p*1 p*2.1 p*3 p*1 p*2.1 p*3<br>pa sgk” W<br>(7) (8)<br>**----- End of picture text -----**<br>


**Figure 4.** Steps to construct GPS rounding boxes. ( **1** ) An original polyline. ( **2** ) Inner points between corner points. ( **3** ) The construction of a rounding box grid. ( **4** ) Mapping a point into its rounding box. ( **5** ) The representation of rounding box of each point with a star symbol. ( **6** ) A guideline for creating the first-layer neighbors of a given rounding box. ( **7** ) The neighbors of the first rounding box. ( **8** ) All neighbors of all rounding boxes. 

Step 1, Figure 4(1): P represents a bus path that is a set of sequence points p from the begin point to the ending point. For example, 

**==> picture [232 x 11] intentionally omitted <==**

Step 2, Figure 4(2): Since most points on polylines are corner points, a distance between adjacent points might be far in case of a long straight line. Thus, we need to find inner points between corner points. The distance of nearby inner points can be adjusted depending on developers, such as 10 m. For example, as with path P in step (1), the inner points between p1 and p2 might be p1.1 and p1.2. Thus, P can be written as follows: 

**==> picture [267 x 11] intentionally omitted <==**

Step 3, Figure 4(3–5): All points of P are rounded into rounding boxes. The rounding digit is customizable by developers. In an area close to the equator such as Thailand, the size of 0, 1, 3, 4, and 5 -digit rounding boxes is approximately 100 km, 10 km, 100 m, 10 m, and 1 m, respectively. For example, if the coordinates of pi are p = (13.13243, 100.47386), the 

_Sustainability_ **2023** , _15_ , 5618 

11 of 23 

3-digit rounding box of p will be p* = (13.132, 100.474). According to step (2), the rounding boxes of the path P is P* in the following line: 

**==> picture [281 x 11] intentionally omitted <==**

Step 4, Figure 4(6–8): The rounding boxes of P* in the previous steps cannot create a continuous route path. In our work, we have to create neighbors of a rounding box in order to connect all rounding boxes and expand the area of a path. The neighbors are created around a box in all directions. A neighbor is defined by p*(x,y), where subscripts x and y are the shifting direction of the current p*. For example, if the three-digit rounding box of p is p* = (13.132, 100.474), the p*(–1,–1) is (13.132–0.001, 100.474–0.001), which becomes (13.131, 100.473). In this case, the original p* is represented by p*(0,0). It means that one-layer neighbors are nine boxes, including the original one. If a developer chooses two-layer neighbors, there will be 25 boxes. Thus, the number of neighbors including the original one is (2 _n_ + 1)[2] , where _n_ is the number of layers surrounded. 

As demonstrated in Figure 4(6,7), the neighbors of the point p*1, including itself, can be p*1(–1,–1), p*1(0,–1), p*1(1,–1), p*1(–1,0), p*1(0,0), p*1(1,0), p*1(–1,1), p*1(0,1), and p*1(1,1). Thus, P**, which is a set of neighbors of elements of P*, as shown in Figure 4(8), can be as follows: 

**==> picture [454 x 12] intentionally omitted <==**

An example of the P** of a route is demonstrated in Figure 5(1), where Figure 5(2) shows rounding points in a zoom-in of the selected rectangle area in Figure 5(1). 

**==> picture [213 x 11] intentionally omitted <==**

**----- Start of picture text -----**<br>
(1) (2)<br>**----- End of picture text -----**<br>


**Figure 5.** Example rounding boxes of a bus route path: ( **1** ) a route path with a selected area; ( **2** ) rounding boxes of the selected area in ( **1** ). 

Thus, the begin point, end point, and polyline of each path in Table 3 are calculated via the rounding boxes and presented in Table 5. In this table, rounding boxes’ data are presented by variables. For clarity, the begin point and the end point refer to the path_id with subfix “.B” and “.E.” For example, in the first entry, R7234.00.B**, R7234.00.E**, and R7234.00** are the sets of rounding boxes of the begin point, the end point, and the polyline, respectively. 

_Sustainability_ **2023** , _15_ , 5618 

12 of 23 

**Table 5.** Example of bus route polyline data with rounding boxes (a point name ending with two-star symbols.) 

|**route**|**path_id**|**path_type**|**direction**|**begin_point**<br>~~**_(Rounding Boxes)_**~~|**end_point**<br>~~**_(Rounding Boxes)_**~~|**polyline**<br>~~**_(Rounding Boxes)_**~~|
|---|---|---|---|---|---|---|
|R7234|R7234.00|main|go|R7234.00.B**|R7234.00.E**|R7234.00**|
|R7234|R7234.01|split|go|R7234.01.B**|R7234.01.E**|R7234.01**|
|R7234|R7234.02|split|back|R7234.02.B**|R7234.02.E**|R7234.02**|
|R7234|R7234.03|sub|go|R7234.03.B**|R7234.03.E**|R7234.03**|
|R7234|R7234.04|sub|back|R7234.04.B**|R7234.04.E**|R7234.04**|
|R8190|R8190.00|main|go|R8190.00.B**|R8190.00.E**|R8190.00**|
|R8190|R8190.01|main|back|R8190.01.B**|R8190.01.E**|R8190.01**|
|. . .|. . .|. . .|. . .|. . .|. . .|. . .|



## 3.3.2. Trajectory Route Matching 

The trajectory route matching is a method to check whether a GPS point is on a path. Since it is unlikely that a coordinate point will be exactly on a path, the distance from the point to the perpendicular line on the path surface is generally considered, as shown in Figure 6(1,2). For this vector technique, a maximum distance should be defined, and it consumes calculation time that is not appropriate with a large amount of data. Thus, we decided to use the rounding boxes of a path for the trajectory route matching. In this figure, b1 is a coordinate of a bus, where a path is a bus route path. Figure 6(3) shows that b1 is rounded into b*1. This location is on a path P if b*1 is an element of P**. The function to detect a point on a route path (POR) is defined in the following equation, where b* is any point and P** is a set of rounding boxes in any path. 

_POR_ ( _b[∗]_ , _P[∗∗]_ 

**==> picture [184 x 23] intentionally omitted <==**

**==> picture [149 x 266] intentionally omitted <==**

**----- Start of picture text -----**<br>
ao b1<br>(1)<br>b1<br>d<br>"<br>(2)<br>b j= *1<br>(3)<br>**----- End of picture text -----**<br>


**Figure 6.** Steps of bus-route matching using GPS rounding boxes. ( **1** ) A location of a bus b1 closing to a polyline of a bus route. ( **2** ) The distance between the bus b1 and the polyline. ( **3** ) The representation of the rounding box of b1, which is b*1, on the neighbors of the rounding boxes of the polyline. 

_Sustainability_ **2023** , _15_ , 5618 

13 of 23 

In addition, to detect a bus driving on a bus route path, we need to verify that most of the GPS coordinates of a bus belong to the route path. The concept of trajectory route matching is a key player for finding QoS scores in the next sections. 

## _3.4. Bus Trip Calculating_ 

When the rounding boxes of all paths constructed, in the next step, it is to detect bus trips and on-path driving. These concepts are described in the following subsections. 

## 3.4.1. Bus Trip Detection 

The concept is to detect when an individual bus transits from the begin point to the end point. The size of the rounding boxes area of a point is about 100 _×_ 100 m, as shown in Figure 7(1). The begin point and end point are defined as follows: 

- The begin point is detected when a bus starts moving out of the rounding boxes area of the begin point, as shown in Figure 7(2). At timestamp t1, a bus is inside the rounding boxes area, while it moves out of the area at the timestamp t2. In this case, t1 is stamped as the time of a bus at the begin point R8190.00.B. 

- The end point is detected when a bus starts moving into the rounding boxes area of the end point, as shown in Figure 7(3). At timestamp t9, a bus is entering the rounding boxes area, and it starts inside the area at timestamp t10. In this case, t10 is stamped as the time of a bus at the end point R8190.00.E. 

**==> picture [466 x 285] intentionally omitted <==**

**----- Start of picture text -----**<br>
begin<br>point<br>end<br>point<br>—= oats<br>rounding<br>—<br>boxes<br>rounding<br>(1) boxes<br>co t1 Cao<br>t2 t10<br>Pomc CĐ m@Đìnnn<br>Cccp Chet coo<br>t9<br>begin  poi nt end  point<br>R8190.00. B<br>| SN...PCCHH =» =rnannimHEH)»_I8 R8190.00.E<br>rTLTLTTL] II<br>UU + ` ——r+—r<br>rounding boxes area ( R8190.00.B ** ) rounding boxes area ( R8190.00.B ** )<br>100 × 100 m 100 × 100 m<br>(2) (3)<br>**----- End of picture text -----**<br>


**Figure 7.** A method to detect a bus at a begin point and an end point. ( **1** ) The rounding boxes of a beginning point and an end point of a bus route path. ( **2** ) A timestamp t1 when a bus starts moving out of a beginning rounding boxes area, which is represented by two-star symbols ( **3** ) A timestamp t10 when a bus enters an end rounding boxes area. 

If the sequence of the begin and end points of a bus, as shown in Figure 8(1), is [R8190.00.B, R8190.00.E, R8190.00.B, R8190.00.B, R8190.00.E], the trips become [(R8190.00.B, 

_Sustainability_ **2023** , _15_ , 5618 

14 of 23 

R8190.00.E), (R8190.00.B, ?), (R8190.00.B, R8190.00.E)]. The first pair and the last pair contain the begin point and the end point of path R8190.00, so they are considered full trips. However, the case (R8190.00.B, ?), which does not have an end point, is not considered a full trip. 

(1) 

**==> picture [15 x 12] intentionally omitted <==**

**==> picture [405 x 212] intentionally omitted <==**

**----- Start of picture text -----**<br>
R8190.00.B R8190.00.E R8190.00.B R8190.00.B R8190.00.E<br>full trip failed trip full trip<br>main sub sub main sub sub split split<br>P.0.B P.2.B P.2.E P.0.E P.2.B P.2.E P.1.B P.1.E<br>AY<br>trip1  ( sub-path trip )<br>trip2 trip3 trip4<br>( main-path trip ) ( sub-path trip ) ( split-path trip )<br>**----- End of picture text -----**<br>


**Figure 8.** Example trip detection from the sequence of begin points and end points. ( **1** ) A chain of trips of an individual buses including full trips and a failed trip. ( **2** ) A chain of trips of an individual bus having sub trip in a trip. 

In a case where a route has main paths, split paths, and subpaths, the main path is considered the highest priority, while the split path and the subpath are in descending order of importance. As shown in Figure 8(2); P.0, P.1, and P.2 are a main path, a split path, and a subpath; and the sequence of a bus is [P.0.B, P.2.B, P.2.E, P.0.E, P.2.B, P.2.E, P.1.B, P.1.E]. The trip is considered [(P.0.B, (P.2.B, P.2.E), P.0.E), (P.2.B, P.2.E), (P.1.B, P.1.E) ], where the first subpath trip (P.2.B, P.2.E) is inside the main path trip, so it is ignored due to the main path having higher priority than the subpath. In this case, there are three trips, (P.0.B, P.0.E), (P.2.B, P.2.E), and (P.1.B, P.1.E). 

The trip calculation results are given in Table 6. In the table, the columns are as follows: 

- **index** : an index, which is a running number, of each entry. 

- **bid** : 

- **path_id** : a path identifier. 

- **begin_ts** : a begin timestamp when a bus starts moving out from a begin point’s rounding boxes area. 

- **end_ts** : an end timestamp when a bus starts moving into an end point’s rounding boxes area. 

- **is_full_trip** : to check if a trip is a full trip, where 1 is a full trip, otherwise 0. 

- **on_path** : a measurement of a bus driving on a route path. It uses a Jaccard index, which will be described in the next subsection. 

_Sustainability_ **2023** , _15_ , 5618 

15 of 23 

**Table 6.** Example trips from the method trip detection. 

|**Index**|**bid**|**path_id**|**begin_ts**|**end_ts**|**is_full_trip**|**on_path**|
|---|---|---|---|---|---|---|
|1|4d43e028|R8190.00|2021-10-01 10:10:00|2021-10-01 12:12:00|1|0.85|
|2|f03235d3|R8190.00|2021-10-01 10:40:00|2021-10-01 12:41:00|1|0.85|
|3|12ec22a7|R8190.00|2021-10-01 11:05:00|2021-10-01 13:07:00|0|0.50|
|4|23731bd3|R8190.00|2021-10-01 11:20:00|2021-10-01 13:22:00|1|0.95|
|5|512e06ff|R8190.00|2021-10-01 11:25:00|2021-10-01 13:28:00|1|0.90|
|6|0a4fd2f5|R8190.00|2021-10-01 11:50:00|2021-10-01 13:52:00|0|0.60|
|7|1b43575e|R8190.00|2021-10-01 12:15:00|2021-10-01 14:14:00|1|0.85|
|8|512e06ff|R8190.00|2021-10-01 13:50:00|2021-10-01 15:56:00|1|0.70|
|9|076fde6b|R8190.00|2021-10-01 15:40:00|2021-10-01 17:49:00|1|0.90|
|10|12ec22a7|R8190.00|2021-10-01 16:05:00|2021-10-01 18:06:00|1|0.95|
|11|23731bd3|R8190.00|2021-10-01 16:35:00|2021-10-01 18:33:00|0|0.70|
|12|4d43e028|R8190.00|2021-10-01 17:20:00|2021-10-01 19:21:00|1|0.95|
|13|23731bd3|R8190.00|2021-10-01 17:50:00|2021-10-01 19:52:00|1|0.90|
|14|f03235d3|R8190.00|2021-10-01 18:20:00|2021-10-01 20:27:00|1|0.85|



The first row in the table indicates that the trip was made by bus “4d43e028” on path R8190.00, which is the main path of route R8190, between 10:10 and 12:12 on 1 October 2022, and was a full trip. In addition, some trips, such as 3, 6, and 11, were considered failed trips, because they did not pass through the end points of their paths. 

## 3.4.2. On-Path Driving Detection 

When a trip is detected, an on-path driving detection is also calculated. The calculation needs to follow the GPS data of each trip point by point to check the distance on a route path and the distance outside of the route path. To do this, a true-positive, falsepositive, and false-negative are verified, as demonstrated in Figure 9, and the Jaccard index is determined. 

- True-positive (TP): the distance of a bus driving on a route path. 

- False-positive (FP): the distance of a bus driving outside of a route path. 

- False-negative (FN): the distance of a route path without a bus driving on it. 

**==> picture [369 x 108] intentionally omitted <==**

**----- Start of picture text -----**<br>
(A) (C)<br>begin<br>(D)<br>point (B) end<br>Oss point<br>"<br>actual route path driving path<br>TP = 5 km FN =5 km TP = 5 km<br>FP = 8 km<br>**----- End of picture text -----**<br>


**Figure 9.** Example GPS tracks of a bus on a bus route path where A–D are points of its polyline. 

After that, the Jaccard index is calculated as in the following equation. As shown in Figure 9, TP is 10 (from 5 + 5), FP is 8, and FN is 5, so the Jaccard calculated by 10/(10 + 8 + 5) is 0.43 or 43%. The maximum is 1 and the minimum is 0. An example result of Jaccard calculation is shown in the column on_path of Table 5. 

**==> picture [254 x 22] intentionally omitted <==**

This step is also used to support the data validation. Attributes on_path and travel time, which is the difference between end_ts and begin_ts, calculated from Table 6 are used to define outliner data. A small value of the on_path, such as a number lower than 0.3, is assumed that a bus trip was not performing its normal duties, so that trip is eliminated 

_Sustainability_ **2023** , _15_ , 5618 

16 of 23 

from the evaluation of QoS. In addition, the outliners of the travel time are detected using the interquartile range (IQR) method [21,22]. Thus, any trip having different travel time than the normal travel time of a given route path is also considered to exclude from the assessment of QoS. 

## _3.5. QoS-1 Score: Tracking Complete Trips_ 

QoS-1 is the score that evaluates the complete trip; in this case, any conditions in Table 4 are applied to the trip data in Table 6. Table 6 includes trips of the path R8190.00, so the condition type “all_trip” of this path, C0013, is applied. This means that the number of trips of path R8190.00 should be 12. QoS-1 is calculated via Equation (7). As the full trips of the path R8190.00 on 1 October 2021 are counted as 11, the QoS-1 score of the path R8190.00 is _max_ (11,12)/12, which is 0.92. 

**==> picture [305 x 25] intentionally omitted <==**

After all paths are calculated, the QoS-1 scores of each route are the weighted average of all paths of that route. For example, the QoS-1 of the route R8190 on 1 October 2021 is shown in Table 7. 

**Table 7.** Example of three QoS scores of the route R8190 on 1 October 2021. 

|**Route**|**Date**|**QoS_1**|**QoS_2**|**QoS_3**|
|---|---|---|---|---|
|R8190|2021-10-01|0.92|0.83|0.70|



## _3.6. QoS-2 Score: Bus On-Path Driving Tracking_ 

Next, the QoS-2 score is calculated by finding the ratio between the number of on-path trips and all trips. The on-path trip is a trip that has the on_path value greater than a specific criterion. Our work chooses 0.85 as a criterion, so, there are 10 on-path trips from Table 6. As well as the on-path trip, all trips are the condition type “all_trip” of a path, as discussed in the QoS-1 score, so all trips of the path R8190.00 is 12. The equation to calculate the QoS-2 score is as follows, where the num_on_path_trips is the number of on-path trips: 

**==> picture [314 x 25] intentionally omitted <==**

In this case, the QoS-2 score of R8190.00 from the example data in Tables 4 and 5 is _max_ (10, 12)/12, or 0.83. This score of a given day is recorded in Table 7. 

## _3.7. QoS-3 Score: Bus On-Schedule Operation Tracking_ 

Lastly, the QoS-3 score is evaluated using condition data in Table 4 and trip data in Table 6. The first step is to select trips from a path and begin time that satisfy the given conditions. Next, the conditions “count” and “headway” are used, and for each condition the steps in the flowchart in Figure 10 are performed. 

In case of a condition type being “count,” the a ratio between max( _n_ , _N_ ) and _N_ is calculated, where _n_ is the number of full trips, and _N_ is the number of possible trips satisfying the condition. According to condition C0014 in Table 4, five trips are needed between 11:00 and 12:00, so _N_ is 5. To apply this condition, indices 3–6 of Table 6 are selected, and the number of trips is 4, so _n_ is 4. Thus, the score of the condition C0014 is 4/5, or 0.8. 

_Sustainability_ **2023** , _15_ , 5618 

17 of 23 

**==> picture [322 x 338] intentionally omitted <==**

**----- Start of picture text -----**<br>
begin<br>select  trips of the given route<br>if trip’s begin_ts  between  condition’s begin_time  and  end _time<br>check<br>con_type<br>con_type = “count” con_type = “headway”<br>N = the number of trips from the condition N = the number of possible trips accroding the<br>headway from the condtion<br>n = the nunber selected trips<br>trip =  first  trip<br>n = 1  if the difference between trip’s begin_ts and<br>condition’s begin_time is acceptable<br>ex_begin_time = trip’s begin_ts<br>trip =  next  trip<br>n = n + 1  if  the difference between trip’s begin_ts<br>and ex_begin_time is acceptable<br>is the last  no<br>trip?<br>yes<br>score = max(n, N) / N<br>store the score value<br>end<br>**----- End of picture text -----**<br>


**Figure 10.** Flowchart for calculating the QoS-3 score. 

In addition, when the condition type is “headway,” a ratio score is calculated the same as for the previous condition. However, _n_ is the number of trips satisfying the headway condition. According to condition C0015 in Table 4, the headway between 16:00 and 18:00 is 30 min, so the first trip must be at 16:00 and the next trips take 30 min each, until 18:00. This means that this condition requires five trips, so _N_ is 5. In this case, a developer can add some error such as _±_ 5 min. Based on the time of this condition, indices 10–13 of Table 6 are selected. 

- At index 10, the begin_time is 16:05, which satisfies the condition including error times. Thus, _n_ is 1, and ex_begin_time is 16:05. 

- At index 11, the begin_time is 16:35. It differs from the ex_begin_time about 30 min, so _n_ becomes 2, and ex_begin_time becomes 16:35. 

- At index 12, the begin_time is 17:20. It differs from the ex_begin_time about 45 min, so this trip is failed. In this case, _n_ is still 2, and ex_begin_time changes into 17:20. 

- At index 13, the begin_time is 17:50, and it differs from the previous one about 30 min. Thus, _n_ becomes 3. 

Since _n_ is 3 and _N_ is 5, the score of this condition is 3/5 or 0.6. At the end, the average score of all conditions, C0014 and C0015, is 0.7. Thus, the QoS-3 score of 0.7 is as recorded in Table 7. 

## **4. Results** 

## _4.1. Result of Bus QoS scores_ 

The GPS transaction dataset of buses between 1 October 2021 and 31 December 2021 was analyzed. There were 709,182,747 transactions in total, including 454 bus routes and 4418 buses. The route numbers were masked due to privacy constraints—for example, 

_Sustainability_ **2023** , _15_ , 5618 

18 of 23 

R7234, R7731, R8196, R8630, etc. After calculating with our approach from the previous section, the daily results of QoS-1, QoS-2, and QoS-3 were as given in Table 8. The table demonstrates examples of 12 entries from the actual 92 entries of route R7234. After that, the QoS scores of each route were grouped by month and reported in Table 9. In addition, the report from Table 9 can be visualized into charts as in Figure 11. There are three charts reporting QoS-1, 2, and 3, and each is grouped by a bus route, where every group displays a QoS score ordered by month. 

**Table 8.** Daily QoS scores of the route R8155 in the 4th quarter of 2021. 

|**Route**|**Date**|**QoS_1**|**QoS_2**|**QoS_3**|
|---|---|---|---|---|
|R7234|2021-10-01|0.83|0.85|0.72|
|R7234|2021-10-02|0.78|0.73|0.76|
|R7234|2021-10-03|0.77|0.80|0.83|
|R7234|2021-10-04|0.83|0.86|0.68|
|R7234|2021-10-05|0.81|0.74|0.73|
|R7234|2021-10-06|0.92|0.75|0.82|
|R7234|2021-10-07|0.84|0.87|0.68|
|R7234|2021-10-08|0.83|0.76|0.80|
||. . .|. . .|. . .|. . .|
|R7234|2021-12-28|0.77|0.91|0.81|
|R7234|2021-12-29|0.75|0.83|0.67|
|R7234|2021-12-30|0.76|0.74|0.82|
|R7234|2021-12-31|0.64|0.82|0.83|



**Table 9.** Monthly QoS scores of various routes for the 4th quarter of 2021. 

|**Route**|**Month**|**QoS_1**|**QoS_2**|**QoS_3**|
|---|---|---|---|---|
|R7234|2021-10|0.86|0.83|0.73|
||2021-11|0.75|0.94|0.81|
||2021-12|0.69|0.87|0.75|
|R7731|2021-10|0.71|0.89|0.72|
||2021-11|0.65|0.93|0.85|
||2021-12|0.73|0.91|0.74|
|R8196|2021-10|0.69|0.88|0.76|
||2021-11|0.87|0.90|0.91|
||2021-12|0.68|0.84|0.67|
|R8630|2021-10|0.73|0.87|0.75|
||2021-11|0.75|0.83|0.89|
||2021-12|0.71|0.83|0.72|



In addition, histograms have been generated to summary QoS scores in detail, as depicted in Figure 12. The _x_ axis is QoS scores from 0 to 100, and the _y_ axis is the number of city bus routes having a particular score. As in the figure, most bus routes have scores close to 100, while a small number of routes have lower scores. In order to make the data more understandable, we graded each route by level: high, medium, low, and lower, as reported in Table 10. The table contains the rating labels, rating range, and number of city bus routes with three QoS scores for each rate. 

_Sustainability_ **2023** , _15_ , 5618 

19 of 23 

**==> picture [271 x 256] intentionally omitted <==**

**----- Start of picture text -----**<br>
1<br>0.8<br>QoS-1 Score 0.60.4<br>0.2<br>0<br>R7234R7234 R7731R7731 R8196R8196 R8630R8630<br>1<br>0.8<br>QoS-2 Score 0.60.4<br>0.2<br>0<br>R7234 R7731 R8196 R8630<br>R7234 R7731 R8196 R8630<br>1<br>0.8<br>0.6<br>QoS-3 Score 0.4<br>0.2<br>0<br>R7234R7234 R7731R7731 R8196R8196 R8630R8630<br>2021-10 2021-11 2021-12 2021-10 2021-11 2021-12 2021-10 -11 2021 2021-12 2021-10 2021-11 2021-12<br>2021-10 2021-11 2021-12 2021-10 2021-11 2021-12 2021-10 021-11 2 2021-12 2021-10 2021-11 2021-12<br>2021-10 2021-11 2021-12 2021-10 2021-11 2021-12 2021-10 2021-11 2021-12 2021-10 2021-11 2021-12<br>**----- End of picture text -----**<br>


**Figure 11.** Charts of monthly QoS scores. 

**==> picture [389 x 68] intentionally omitted <==**

**----- Start of picture text -----**<br>
QoS-1 QoS-2 QoS-3<br>300 QoS-1 300 =S-2 400 QoS-3<br>250 350<br>250<br>300<br>200 200 250<br>all scores 150 10 200<br>**----- End of picture text -----**<br>


**==> picture [48 x 8] intentionally omitted <==**

**----- Start of picture text -----**<br>
scores < 80<br>**----- End of picture text -----**<br>


**Figure 12.** Histograms of QoS scores. Each column is the QoS score; the first row shows histograms of all scores, and the second row displays histograms of scores below 80. 

**Table 10.** Number of city bus routes having each rating level of QoS scores. 

|**Rating**|**Score**||**Number of City Bus Routes**||
|---|---|---|---|---|
|**Label**|**Range**|**QoS_1**|**QoS_2**|**QoS_3**|
|High|90–100|313|315|417|
|Medium|80–90|10|37|14|
|Low|60–80|40|66|9|
|Lower|0–60|91|36|14|



_Sustainability_ **2023** , _15_ , 5618 

20 of 23 

## _4.2. Discussion_ 

The measurement of QoS of public city bus transportation is an early step in the improvement of smart mobility since it helps one to understand the current situation. There are many factors involved in the assessment, such as accessibility, availability, comfort, customer satisfaction, reliability, safety, security, etc. [2–5]. These metrics are generally evaluated by the user survey method [2–4], because users are the direct service consumers and this method can reflect user expectations in a straightforward way. As we are in the era of data utilization, data analytics supports the analysis of certain factors, in addition to the survey method [6,8]. Some studies have attempted to use GPS data analytics for transportation, e.g., for assessing the travel time, travel time variability, waiting time, or transfer time of buses [7,9]. This is advantageous evidence of the use of data for determining the QoS of transportation, especially bus services. Since several studies have addressed the transportation-related issues mentioned above, this study is an extension of the analysis of GPS data to measure the efficiency of bus services in terms of accessibility, availability, and reliability. Thus, we aimed to measure the QoS of public city bus transportation in Bangkok by analyzing the GPS data of buses, route data, and schedule conditions. We used three QoS scoring functions to determine complete trips, on-path driving, and on-schedule operations, tracking the conditions of each bus route. The results are reported in Section 4.1; we found that most of the bus routes received high scores. In this discussion, we organize our contribution into two parts: our approach, and smart city management. 

First, the contribution of the proposed approach is to derive the quality of service of bus transportation by data analytics. As mentioned in the introduction, it would be convenient if there were data from wireless sensors at each bus stop to detect the bus arrival time [15,16]. However, without wireless sensor data, it was necessary to use GPS and spatial data. For the datasets that we have, we found four challenging issues: that were no arrival data at any bus stops, one bus route had many paths, a bus could choose any path under the same route, and there was no exact departure time in timetables. Therefore, the GPS coordinates rounding box was adopted for path matching [17–20]. It rasterizes a vector of a polyline into a set of grids, which are indices of a path. Although this technique requires some memory, it involves little computational processing, and is capable of working with a large amount of data, such as voluminous GPS transaction coordinates. To match a path, it finds a trip of a bus with a path type and a direction, so we could detect incomplete trips, as demonstrated in Figures 7 and 8. Another advantage of using rounding boxes is that it is simple to detect a bus driving along a route, as shown in Figure 9. Moreover, working with a condition table and the algorithm in Figure 10, we could correct the frequency and headway of each bus route path. For all of these steps, the rounding box technique is a key player that preprocesses the raw data into bus trips and serves all QoS scoring functions. The results of our work demonstrate the use of data analytics to monitor QoS, in addition to surveys, as other works have demonstrated. There are more criteria that data analytics can support, such as driving safety, travel time, bus stop proximity, other mode connections, etc.; however, this requires much more data, such as bus stop locations and the coordinates of other modes, which are useful for future research. In addition, the survey method from [2,3,5,6] is still needed because some qualitative results, such as user satisfaction, on-board safety, appropriate fare, driver’s ability, and ticket availability are difficult to measure by data analytics. 

Second, our contribution to smart city management was to use data to improve the QoS. Our work focused on public city bus transportation because buses are commonly used in any city, such as Bangkok, Thailand. Our data analytics contributes to the research on transport quality in terms of reliability, accessibility, and availability. 

**Reliability** . The reliability is one aspect contributing to user satisfaction [23]. This factor can refer to an ability to carriage passengers from a starting point to an end point [24]. The reliability assessed in this work is the ability of buses to perform their intended trip from an origin to a destination along a route path under specified conditions for a given period without failure. This factor is measured by QoS-1, which is for compete trip tracking. 

_Sustainability_ **2023** , _15_ , 5618 

21 of 23 

This metric will ensure that bus providers provide enough buses to offer the number of complete trips that they have committed to. A low score means that the bus operator cannot provide enough buses to complete the agreed number of trips, so the operator must prepare more vehicles; otherwise, it may negatively affect the use of this bus route in the future. The results in Table 10 show that more than 300 bus routes achieved a high rating, while about 130 needed significant improvement. 

**Accessibility** . The term “accessibility” generally refers to the ability to transfer people from an origin to a destination [25]. This measurement approach is primarily from the perspective of user demand and can be viewed as the coverage of transportation system against the needs of people and user satisfaction [26]. The evaluation in a user-centric mode is possible by the user survey method [2–4], and by data analytics from individual trip data such as inferring the mobility of people from their bus smart card payment transactions to evaluate the supply of public bus transport. In our work, there are data from the supply side only. The information contains the routes that operators take as concessions from the government authority and conditions for running buses on each route path that the operators have committed to. In this work, we excluded how the route meets the user demand; nevertheless, we were able to evaluate how buses drive along the promised route paths. Since QoS-1 measures complete trips, a bus may go off route to achieve the fastest trip between a begin point and an end point in order to increase the QoS-1 score. This results in a bus not stopping at every location on the route, and is considered a violation of the regulations of the city bus transportation. Thus, QoS-2, for bus on-path driving tracking, was introduced to confirm that a bus driver follows the whole route path. A high score means that a trip had less off-route time and covered the whole path. As per our analysis, there were about 300 bus routes rating highly, whereas for about 100 the operator must enforce stricter guidelines with the drivers in order to increase the QoS-2. 

**Availability** . The availability of for public transportation refers to the ability to provide services covering the demands of travels from passengers. It can be viewed that having a bus service in accordance with the schedule is a part of the term availability [27–29]. In this case, work interprets the availability in terms of the regularity of bus operation by QoS-3, which is for bus on-schedule operation tracking. Even if a bus line has completed the number of trips specified and did not go off route, it cannot be guaranteed that all buses will operate regularly. According to the frequency and headway of the bus operation agreed upon by the operator, each bus line must operate as promised. A failed condition leads to a lower QoS-3 score. A high score allows users the confidence to use the bus according to their demands. The results in Table 10 indicate that most bus routes were reliable in terms of on-schedule operation. Compared to the previous QoS scores, not many bus routes needed improvement in QoS-3. If we take a closer look at the analytical results, we see that many bus routes operated more trips than promised. This situation is beneficial for users, and causes a higher QoS-3 score as a by-product. However, this metric can be enhanced to evaluate the waiting time at each bus stop. In this case, an individual timetable is required for every bus stop. 

Our proposed method for scoring the QoS of bus transportation is evidence in support of having policies to enhance smart mobility. Policy makers need to consider the data carefully, because policies that benefit some service consumers may adversely affect other groups of people [10]. We have primarily presented the analysis of GPS data from the supply side, without taking demand-side data into consideration. In the future, when there are data on people’s need for trips in Bangkok, not just acquired through the survey method, such as transactions from all-in-one smart cards for public transportation [9], location data from smartphones [25], etc., we may be able to glean more insights from both the demand side and the supply side to optimize bus route networks [30] and schedules [31]. In this event, policies about smart card and privacy data must be put into place. 

To this end, our work demonstrates the power of having quality GPS data and spatial data that enable policy makers to bring about positive changes in a city. We can say that our 

_Sustainability_ **2023** , _15_ , 5618 

22 of 23 

contribution encourages the sustainability of public city bus transportation and, as such, can be a part of better living in the future. 

## **5. Conclusions** 

This work introduces an approach to the measurement of the quality of service (QoS) of public city bus transportation in Bangkok in terms of reliability, accessibility, and availability, using global positioning system (GPS) data analytics. There were three QoS scoring functions: QoS-1 for complete trip tracking, QoS-2 for bus on-path driving tracking, and QoS-3 for bus on-schedule operation tracking. The analytical process had four phases: input, preprocessing, scoring, and output. Input data were GPS transactions of buses from the last quarter of 2021; route data containing polylines of all route paths of city buses in Bangkok and its metropolitan area; and schedule conditions of each route path. The challenges involved in this study were no bus arrival timestamp at each bus stop, one route having many paths, no fixed path of buses on the same route, and no departure time being given in the schedule. Thus, we had to detect the trips on each route by analyzing GPS trajectory data and path polylines. In this case, GPS coordinates rounding became an important technique of the preprocessing phase. In the next phase, scoring, when trips and their metadata were detected, the three QoS scoring functions were executed and gave results as scores in the output phase. The analytical results of all routes showed that most bus routes have high scores; however, some bus routes need to be improved due to low scores. Thus, the contribution of our work was to demonstrate the feasibility of using data analytics to measure the QoS of bus transportation, in addition to using a survey method. This is one of the tasks that can contribute to the sustainability of smart cities. 

Due to this work focusing on the analytics of bus tracking data from the supply side, in the future, there needs to be more data, such as individual payment transactions for public transportation and individual journey data from smartphones, to improve QoS methods against the demand side. 

**Author Contributions:** Conceptualization, R.C., A.S. and T.T.; Methodology, R.C. and T.T.; Formal analysis, R.C.; Resources, A.S.; Data curation, T.T.; Writing—original draft, R.C.; Writing—review & editing, T.T.; Visualization, R.C.; Supervision, A.S.; Project administration, A.S. All authors have read and agreed to the published version of the manuscript. 

**Funding:** This research received no external funding. 

**Institutional Review Board Statement:** Not applicable. 

**Informed Consent Statement:** Not applicable. 

**Data Availability Statement:** Not applicable. 

## **References** 

1. Hansson, J.; Pettersson, F.; Svensson, H.; Wretstrand, A. Preferences in regional public transport: A literature review. _Eur. Transp. Res. Rev._ **2019** , _11_ , 1–16. 

2. Wethyavivorn, P.; Sukwattanakorn, N. Problems and barriers affecting sustainable commuting: Case study of people’s daily commute to Kasetsart University, Bangkok, Thailand. _IOP Conf. Ser. Earth Environ. Sci._ **2019** , _329_ , 012011. 

3. Ueasangkomsate, P. Service quality of public road passenger transport in Thailand. _Kasetsart J. Soc. Sci._ **2019** , _40_ , 74–81. 

4. Chan, W.; Ibrahim, W.W.; Lo, M.; Suaidi, M.; Ha, S. Sustainability of public transportation: An examination of user behavior to real-time GPS tracking application. _Sustainability_ **2020** , _12_ , 9541. 

5. Page, S.; Yue, G.G. Transportation and tourism: A symbiotic relationship? In _The SAGE Handbook of Tourism Studies_ ; Sage Publications: Thousand Oaks, CA, USA, 2009; pp. 371–395. 

6. Goyal, S.; Agarwal, S.; Singh, N.S.S.; Mathur, T.; Mathur, N. Analysis of Hybrid MCDM Methods for the Performance Assessment and Ranking Public Transport Sector: A Case Study. _Sustainability_ **2022** , _14_ , 15110. 

7. Mazloumi, E.; Currie, G.; Rose, G. Using GPS data to gain insight into public transport travel time variability. _J. Transp. Eng._ **2010** , _136_ , 623–631. [CrossRef] 

8. Shen, L.; Stopher, P.R. Review of GPS travel survey and GPS data-processing methods. _Transp. Rev._ **2014** , _34_ , 316–334. 

_Sustainability_ **2023** , _15_ , 5618 

23 of 23 

9. Gschwender, A.; Munizaga, M.; Simonetti, C. Using smart card and GPS data for policy and planning: The case of Transantiago. _Res. Transp. Econ._ **2016** , _59_ , 242–249. [CrossRef] 

10. Liu, Q.; Liu, Z.; Kang, T.; Zhu, L.; Zhao, P. Transport inequities through the lens of environmental racism: Rural-urban migrants under Covid-19. _Transp. Policy_ **2022** , _122_ , 26–38. 

11. Chawuthai, R.; Pruekwangkhao, K.; Threepak, T. Spatial-Temporal Traffic Speed Prediction on Thailand Roads. In Proceedings of the 7th International Conference on Engineering, Applied Sciences and Technology, Pattaya, Thailand, 1–3 April 2021; pp. 58–62. 

12. Chawuthai, R.; Chankaew, N.; Threepak, T. A Hybrid Method for Predicting a Potential Next Rest Stop of Commercial Vehicles. _Transp. Res. Procedia_ **2018** , _34_ , 36–43. [CrossRef] 

13. Chawuthai, R.; Ainthong, N.; Intarawart, S.; Boonyanaet, N.; Sumalee, A. Travel Time Prediction on Long-Distance Road Segments in Thailand. _Appl. Sci._ **2022** , _12_ , 5681. 

14. Chawuthai, R. Monitoring roadway lights and pavement defects for nighttime street safety assessment by sensor data analysis and visualization. _Sens. Mater._ **2018** , _30_ , 2267–2279. [CrossRef] 

15. SL, A.H.; Samsudeen, S.N. Real time bus tracking and scheduling system using wireless sensor and mobile technology. _J. Inf. Syst. Inf. Technol._ **2016** , _1_ , 18–23. 

16. Kamble, P.A.; Vatti, R.A. Bus tracking and monitoring using RFID. In Proceedings of the 2017 Fourth International Conference on Image Information Processing, Shimla, India, 21–23 December 2017; pp. 1–6. 

17. Huang, S.-H.; Lin, C.-S. Rapid Route Comparison Based on GPS Coordinates and Bounding Boxes. _J. Traffic Logist. Eng._ **2019** , _7_ , 5–9. [CrossRef] 

18. Elevelt, A.; Bernasco, W.; Lugtig, P.; Ruiter, S.; Toepoel, V.; Ruiter, B.M.S. Where you at? Using GPS locations in an electronic time use diary study to derive functional locations. _Soc. Sci. Comput. Rev._ **2021** , _39_ , 509–526. [CrossRef] 

19. Ciociola, A.; Cocca, M.; Giordano, D.; Vassio, L.; Mellia, M. E-scooter sharing: Leveraging open data for system design. In Proceedings of the 2020 IEEE/ACM 24th International Symposium on Distributed Simulation and Real Time Applications (DS-RT), Prague, Czech Republic, 14–16 September 2020; pp. 1–8. 

20. Payyanadan, R.P.; Sanchez, F.A.L.; Lee, J.D. Assessing route choice to mitigate older driver risk. _IEEE Trans. Intell. Transp. Syst._ **2016** , _18_ , 527–536. 

21. Yang, J.; Rahardja, S.; Fränti, P. Outlier detection: How to threshold outlier scores? In Proceedings of the International Conference on Artificial Intelligence, Information Processing and Cloud Computing, Sanya, China, 19–21 December 2019; pp. 1–6. 

22. Rilett, L.R.; Tufuor, E.; Murphy, S. Arterial roadway travel time reliability and the COVID-19 pandemic. _J. Transp. Eng. Part A Syst._ **2021** , _147_ , 04021034. 

23. Soza-Parra, J.; Raveau, S.; Muñoz, J.C.; Cats, O. The underlying effect of public transport reliability on users’ satisfaction. _Transp. Res. Part A Policy Pract._ **2019** , _126_ , 83–93. 

24. Xiaoliang, Z.; Limin, J. Analysis of Bus Line Operation Reliability Based on Copula Function. _Sustainability_ **2021** , _13_ , 8419. 

25. Liu, Q.; An, Z.; Liu, Y.; Ying, W.; Zhao, P. Smartphone-based services, perceived accessibility, and transport inequity during the COVID-19 pandemic: A cross-lagged panel study. _Transp. Res. Part D Transp. Environ._ **2021** , _97_ , 102941. 

26. Curl, A.; Nelson, J.D.; Anable, J. Does accessibility planning address what matters? A review of current practice and practitioner perspectives. _Res. Transp. Bus. Manag._ **2011** , _2_ , 3–11. [CrossRef] 

27. Leng, N.; Corman, F. The role of information availability to passengers in public transport disruptions: An agent-based simulation approach. _Transp. Res. Part A Policy Pract._ **2020** , _133_ , 214–236. 

28. Vdovychenko, V.; Ivanov, I.; Pidlubnyi, S. Assessment of the impact of traffic conditions on the availability of transport services of the city bus route. _Technol. Audit. Prod. Reserves_ **2022** , _3_ , 45–50. 

29. L’upták, V.; Dro´zdziel, P.; Stopka, O.; Stopková, M.; Rybicka, I. Approach methodology for comprehensive assessing the public passenger transport timetable performances at a regional scale. _Sustainability_ **2019** , _11_ , 3532. 

30. Zhang, H.; Cui, H.; Shi, B. A data-driven analysis for operational vehicle performance of public transport network. _IEEE Access_ **2019** , _7_ , 96404–96413. [CrossRef] 

31. Zhu, H.; Wu, Y.; Wang, Y. Algorithm for Headway of Fixed Route Buses in Bus Stations Based on Bus Big Data. In Proceedings of the 6th International Conference on Transportation Information and Safety, Wuhan, China, 22–24 October 2021; pp. 28–33. 

**Disclaimer/Publisher’s Note:** The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content. 

