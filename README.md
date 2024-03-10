<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->




<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ECE750-Group-5/Adaptive-Circuit-Breaking">
    <img src="https://lh7-us.googleusercontent.com/ytKlHDXHdyiDhGdQA3UcjGxBJ24YBfpREVdVmjyrLy-VsbIwA4s5hQ5h448I3fX9bNUE9qQsKrI26Ig1bbh_ep7G-Dxyi5tF07tUMEl9np0kVVpRu-nKhVG_QNS-Omcr5iqu5jUYQrqpZwe6Cv0S=s2048" alt="Logo" width="250" height="250">
  </a>

  <h3 align="center">Proactive Circuit Breaking For Istio </h3>
  <p align="center">
    Inspired by TCP Reno and the Adaptive Concurrency Limit feature of the Envoy Proxy
    <br />
    <a href="https://docs.google.com/presentation/d/e/2PACX-1vSXUGH3mD93rpFue1jKB7sdrWB7V2XYQYAegnisOGFjAaB945cX5yPdAArM4oRm5SrgRrQA0ANQBCOD/pub?start=false&loop=false&delayms=3000"><strong>Explore our presentation »</strong></a>
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
    <li><a href="#limitations">Limitations</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

### Motivations
We got the idea from two sources. First, [Mendonça and etc.](#references) in their survey paper about building self-adaptive microservice systems, mentioned how the self-adaptive methods could make todays' cloud native applications more resilient. In this paper, they pointed out a research topic for self-adaptive circuit breakers.

Second, Netflix Engineering Blog has a famous article, *[Performance under Load](#references)*, which states how circuit breakers can keep the downstream services get overwhelmed and mitigate the cascading failures.


### Problem Statement
Because of runtime uncertainty and frequent code changes, it is hard to set the right circuit breaking thresholds. The traditional circuit breaking methods are not adaptive to the runtime changes.

The Envoy Proxy has a feature called Adaptive Concurrency Limit, which is a real-time adaptive circuit breaking mechanism. Inspired by TCP Vegas, a latency-based TCP congestion control algorithm,  It uses the latency as a feedback to adjust the concurrency limit. However, this feature is not available in Istio ([Istio Issue 25991](https://github.com/istio/istio/issues/25991)), which is a popular service mesh platform.

The Envoy implementation have to recalibrate the latency when the concurrency limit is 1 for every measure window, introducing parameters for extra tuning and artificial unavailability. 



### Solution
Our solution intends to solve this problem by mimicking the TCP Reno congestion control algorithm and use CPU utilization, a more immediate signal for saturation, as the feedback. 

#### High-Level Design
<img src="https://lh7-us.googleusercontent.com/qkVgRBU2SrYRMWuea8pYPwMHsmJoafSCULGwaxCGeyU0xD7EdJFCCSKHwPIrP6_0E5BGmxhMVwRpOx8ZzW8Xix_2ZJdNqERM-jDklQc-Wf0Pi2hLpHW3inCiPTcU75tRUR9ASTmwqAo_RQ4QuMlN=s2048" alt="architecture" >

#### State Machine Algorithm
* Multiplicative Decrease Multiplicative Increase
* Random Probing
<img src="https://lh7-us.googleusercontent.com/NZfRzJL8VUw2ujsP9FkUMgIltP0vANbxGGg9SKvBH4ZHPmMD1TAHmKPobtxPKnRTnAXxAnuKKgvf9owk9SMrn8yqDSTkLpMyoKTpACwzxM7XNJQwF-5j9mdQS243swO7Fr0dEmhubjn8XBJ74wGB=s2048" alt="state machine" >

### Experiment
#### Experiment Setup
We have three experiment group: Group A with proactive Circuit Breaking (timeline 21:50 to 22:00), Group B without any Circuit Breaking (timeline 22:00 to 22:20), and Group C with static Circuit Breaking with a predefined concurrency limit of 10 (timeline 22:25 to 22:35). For each group, we used Fortio to generate a constant load of 140 QPS and a HttpBin container as our target service with a constant resource of 20m CPU amd 78 Mi memory. We used Prometheus and Grafana to monitor the CPU utilization and the QPS of the target service.

#### Results
<img src="https://lh7-us.googleusercontent.com/hFH1dR0oIpb-lGYJqqCdj8PddPoTnevS2NT7U8VzdqGg522wugPSmRdME8bvnSkJMvg_KVd6fnHL_SEjSbQvwM-rImTpDU3v1n-t8Co7P_XR2dYTW4ZuWhNlWTK_6-TUuZSYNm8z_lkl32-7lTzz=s2048" alt="CPU utilization" >
<img src="https://lh7-us.googleusercontent.com/g09fpMZIXgKj3Kp8PZyC5RG_5dEvPfW1JJreogxO3HajbgCzORMIPys6T0sMdCD-Yfn26SrnN72G17-HQ-VGNzKnz3n7LUMGTPHrjKbd9Qx73zYYZPGDhgsQDxveCaYW9swyhvEBwcXXQ3cgYouC=s2048" alt="CPU utilization" >

Both CPU and Latency improves. However, the latency didn't improve as much as we expected. We will need to further investigate the root cause of the high variance.


### Built With
* [Istio](https://istio.io/)
* [Kubernetes](https://kubernetes.io/)
* [Fortio](https://fortio.org/)
* [Httpbin](https://httpbin.org/)
* [Prometheus](https://prometheus.io/)
* [Grafana](https://grafana.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started
### Prerequisites
You need to have minikube installed. If you don't have it, you can install it by following the instructions [here](https://minikube.sigs.k8s.io/docs/start/).

### Installation
1. Install Prometheus Operator, Prometheus, CAdvisor, Fortio and Grafana
In the root directory, run the following command:
```sh
chmod +x set-up.sh
./set-up.sh
```

2. Configure the receiver for Prometheus AlertManager (Optional)
 This is example for Slack. You can use other receivers as well.
```sh
kubectl apply -f monitoring/alert
```

1. Deploy Httpbin
```sh
kubectl apply -f httpbin/httpbin.yaml
```

4. Start the proactive circuit breaker MAPE loop
```sh
python3 analyzing_planning_executing/main.py
```

5. Start Fortio load test
```sh
kubectl exec "$FORTIO_POD" -c fortio -- /usr/bin/fortio load -c 140 -qps 140 -n 60000 -loglevel Warning http://httpbin:8000/get
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>




## Limitations
* The current implementation is a proof of concept and is not production ready.
* We haven't tested the system for system degradation and scaling-out events.
* We could adopt the cubic increase function from TCP Cubic for  more efficient adaptations.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
This project was developed as part of the ECE750 course at the University of Waterloo. We would like to thank our instructors, Prof. Landan and the TAs, for their guidance and support throughout the term.

We used DALLE to generate our project logo and Copilot for generating documentations.

## References
1. “Circuit Breaking.” n.d. Istio. Accessed December 1, 2023. https://istio.io/latest/docs/tasks/traffic-management/circuit-breaking/.
2. Mendonça, Nabor C., Pooyan Jamshidi, David Garlan, and Claus Pahl. "Developing self-adaptive microservice systems: Challenges and directions." IEEE Software 38, no. 2 (2019): 70-79.
3. Yanacek , David. n.d. AWS. Accessed December 1, 2023. https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/.
4. Landau, Eran, William Thurston, and Tim Bozarth. 2018. “Performance under Load.” Medium. Netflix Technology Blog. March 23, 2018. https://netflixtechblog.medium.com/performance-under-load-3e6fa9a60581.
5. Netflix Opensource Software. 2023. “Concurrency  Limit.” GitHub. November 29, 2023. https://github.com/Netflix/concurrency-limits/tree/master.
6. Allen, Tony. 2020. “Envoy, Take the Wheel: Real-Time Adaptive Circuit Breaking.” Www.youtube.com. September 4, 2020. https://www.youtube.com/watch?v=CQvmSXlnyeQ.
7. Allen, Tony. 2019. “Envoy GitHub Issue #7789: Adaptive Concurrency Control L7 Filter.” GitHub. July 31, 2019. https://github.com/envoyproxy/envoy/issues/7789.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


