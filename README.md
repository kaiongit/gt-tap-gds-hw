# URL Shrinker
> Made for **GovTech GDS - ENP** & **DCUDE**'s technical assessment.

Try the application at 
[https://nomadic-thinker-355706.et.r.appspot.com/](https://nomadic-thinker-355706.et.r.appspot.com/).

<p align="center">
  <img src="./example.gif" alt="Example use of application">
</p>

### Outlined objectives and what was achieved
- [x] Create a backend API server for conversion of URL
- [x] Create a frontend application to allow use of API
- [x] Store the converted URLs in a ~~relational~~ database 
- [x] Style the frontend and make its mobile responsive
- [x] Deploy the application to the cloud
- [ ] Write some unit tests

### Overall system architecture
![Overall system architecture of application](/overview.png)
The application is designed cloud first. The whole application runs on the Google Cloud platform. 
The APIs are implemented as microsevices. The URL Shrinker API and URL Expander API are each their 
own Google Cloud Functions. The front end application is a Single Page Application and runs on 
Google's App Engine. The underlying datastore for the application is in Firestore. Firestore is not
the best choice for this application, but is the \~most appropriate\~ amongst the 
[Google Cloud free tier offerings](https://cloud.google.com/free). The whole application is kept 
within Google Cloud for another practical reason - authentication is automatic between the services.

### Libraries used
#### Frontend
- [Skeleton](http://getskeleton.com/)
- [Flask](https://pypi.org/project/Flask/)
#### Backend
- [Flask](https://pypi.org/project/Flask/)
- [RandomWords](https://pypi.org/project/RandomWords/)
- [google-cloud-firestore](https://pypi.org/project/google-cloud-firestore/)

Made with :purple_heart: and :coffee: in Singapore.