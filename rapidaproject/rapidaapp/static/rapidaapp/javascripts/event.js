function ajax_call(formData){
    $.ajax({
        type: 'POST',
        url: "ajax_find/",
        data: formData,
        headers: {
          'Cross-Origin-Opener-Policy': 'same-origin'
        },
        success: function(response) {
          var dataListDict = response.dataListDict;
          var dataListTuple = response.dataListTuple;
          var field = response.field;
          //console.log(dataListDict);
          var data_head_node = document.getElementById("data-head")
          var data_head = $("#data-head");
          var data_body = $("#data-body");
          

          if (data_head_node.childNodes.length <= 1){
              $.each(dataListDict[0], function(key, value){
                  //console.log(key + ': ' + value)
                  //data_head.append("<th>" + key + "</th>");
                  var newTh = document.createElement("th");
                  newTh.innerHTML = key  
                  data_head.append(newTh); 
              });
          }


          var data_body_node = document.getElementById("data-body");
          //console.log(data_body_node.childNodes.length);
          var firstChild = data_body_node.firstChild;
          firstChild.innerHTML = "fafao"
          var parentWithChild = document.querySelector("[class] > .dataTables_empty");
          //console.log(parentWithChild.parentNode);
          if (parentWithChild){
              data_body_node.removeChild(parentWithChild.parentNode);
          }

          //loop through each line
          var check_before_add = []
          for (let i = 0; i < data_body_node.rows.length; i++) {
              let row = data_body_node.rows[i]; // get the i-th row
              //console.log(row.cells[1].textContent);
              let input = row.cells[1].querySelector("input");
              let inputValue = input.value;
              //console.log(inputValue)
              check_before_add.push(inputValue); 
              for (let j = 0; j < row.cells.length; j++) {
                  //let cell = row.cells[j]; // get the j-th cell in the row
                  let cell = row.cells[1];
                  // do something with the cell, for example:
                  //console.log(cell.textContent); // get the text content of the cell       
              }
          }

          console.log(check_before_add);
          console.log( data_body_node.rows.length)

          var newTr = document.createElement("tr");
          var newTd = document.createElement("td");
          newTd.innerHTML = "";
          newTr.appendChild(newTd); //this is the first empty col 
          
          var j=0;
          $.each(dataListDict[0], function(key, value){
              //console.log(key + ': ' + value)
              //data_body.append("<td>" + value + "</td>");
              var aTd = document.createElement("td");
              if (key == 'Numero_d_envoi') {
                  let input = document.createElement("input");
                  input.setAttribute("type", "text");
                  input.setAttribute("id", value);
                  input.setAttribute("value", value);
                  input.setAttribute("name", "numEnvoi-"+(data_body_node.rows.length+1));
                  input.readOnly = true;
                  aTd.appendChild(input);
              }else if(key == 'Action'){
                  let button = document.createElement("button");
                  button.innerHTML = "X";
                  button.value = value;//same as Numero_d_envoi
                  aTd.appendChild(button);
                  button.addEventListener("click", function() {
                      let r = confirm("Retirer du tableau?");
                      if (r == true) {
                          let parent = this.parentNode;
                          let grandParent = parent.parentNode;
                          grandParent.remove();
                      }
                  });     
              }else{                   
                  aTd.innerHTML = value
              }               
              newTr.appendChild(aTd);    
          });

          //Do not add added numEnvoi and empty input field
          $.each(dataListDict[0], function(key, value){
              if (key == 'Numero_d_envoi') {
                  if (check_before_add.includes(value)) {
                      alert(`${value} déjà ajouté.`);
                  } else {
                      data_body_node.appendChild(newTr);
                  }
                  document.getElementById("numEnvoi").value = "";
              }   
          });

          
        },
        error: function(error) {
          console.error('Error submitting post:', error);
        }
      });    
}

function ajax_add_call(formData){
    $.ajax({
        type: 'POST',
    url: "ajax_add/",
    data: formData,
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin'
    },
    success: function(response) {
      txt_envois = ""
      for (var i = 0; i < response.modification.length; i++) {
          txt_envois = txt_envois + ',' + response.modification[i]
      }
      alert(txt_envois.slice(1) + " sont mis à jour.");
      //message_tag = $("#message").html(txt_envois.slice(1) + " sont mis à jour.");
      var data_body_node = document.getElementById("data-body");
      var newTr = document.createElement("tr");
      input.setAttribute("class", "dataTables_empty");
      var newTd = document.createElement("td");
      newTd.innerHTML = "Aucunne données";
      newTr.appendChild(newTd); 
      data_body_node.innerHTML = "";
      data_body_node.appendChild(newTr);
    },
    error: function(error) {
      console.error('Une Erreur lors de la soummission:', error);
    }
  });
}

$(document).ready(function(){
    $('#form_search2').submit(function(e) {
        e.preventDefault();
    
        var formData = $(this).serialize();
    
        ajax_call(formData);
    });//End form_search2 submit

    $('#form_search3').submit(function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        //var formData = {'numEnvoi':'numfake', 'bureauOrigine':10101, 'bureauPasse':10102, 'statut':'B', 'isActive':1, 'chemin':10103, 'parcours':10102, 'dateHistorique':'2023-02-15', 'burSuiv':10103, 'burPrec':10101, 'dateHistoriqueFull':'2023-02-15:10:01:01'};
        ajax_add_call(formData)
    });
    

    // Select the button element
    var resetButton = document.getElementById('resetEventC');

    // Add an event listener for button click
    resetButton.addEventListener('click', function(e) {
        // Perform some action when the button is clicked
        //console.log('Button clicked!');
        location.reload("event/");
    }); 

    
});

