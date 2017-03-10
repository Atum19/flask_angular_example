(function () {

  "use strict";

  angular.module("WordcountApp", [])

  .controller("WordcountController", ["$scope", "$log", "$http", "$timeout",
    ($scope, $log, $http, $timeout) => {

    $scope.getResults = () => {

      $log.log("test");

      // get the URL from the input
      var userInput = $scope.url;

      // fire the API request
      $http.post('/start', {"url": userInput}).then((results) => {
          $log.log(results);
          getWordCount(results.data);

        }, (error) => {
          $log.log(error);
        });

    };

    function getWordCount(jobID) {

      var timeout = "";

      var poller = () => {
        // fire another request
        $http.get("/results/"+jobID).then((data, status, headers, config) => {
            if(status === 202) {
              $log.log(data, status);
            } else if (status === 200){
              $log.log(data);
              $scope.loading = false;
              $scope.submitButtonText = "Submit";
              $scope.wordcounts = data;
              $timeout.cancel(timeout);
              return false;
            }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            timeout = $timeout(poller, 2000);
          }, (error) => {
            $log.log(error);
            $scope.loading = false;
            $scope.submitButtonText = "Submit";
            $scope.urlerror = true;
          });
      };
      poller();
    }

  }
  ]);

}());
