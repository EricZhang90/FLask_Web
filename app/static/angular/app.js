var mainApp = angular.module("mainApp", []);


mainApp.controller('postController', function($scope) {
    $scope.backendData = {
        postings:[
        {body: "", timestamp: ""}
        ]
    };
});
