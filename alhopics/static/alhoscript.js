  var static_loc       = "../static/"

  function settextcolor(name,col)
  {
    document.getElementById(name).style.color = col;
  }

  function anim_image(cam_id, i)
  {
    //console.log("anim_image: " + cam_id + ", " + i);

    if (current_idx[cam_id] == i)
      return;

    if (current_idx[cam_id] >= 0)
    {
      settextcolor("cam" + cam_id + "_txt_" + current_idx[cam_id],'#0000ff');
    }

    settextcolor("cam" + cam_id + "_txt_" + i,'#ff0000');
    document.getElementById("cam" + cam_id + "_image").src = static_loc + images[cam_id][i]['filelocation'];
    current_idx[cam_id] = i;
  }

  function updateLightControl()
  {
    $.ajax({
      type: "GET",
      url: "api/events",
      data: { format: 'json', type: "light" },
      success: function(response)
      {
        console.log("executed: " + response);
        buildHtmlTable(response, "#lightcontrol");
      }
    });
  }

  function updateMovement()
  {
    $.ajax({
      type: "GET",
      url: "api/events",
      data: { format: 'json', type: "movement" },
      success: function(response)
      {
        console.log("executed: " + response);
        buildHtmlTable(response, "#movement");
      }
    });
  }

  function lightsOn()
  {
    $.ajax(
    {
      type: "GET",
      url: "api/light",
      success: function(response)
      {
        console.log("success: " + response['success']);
      }
    });
  }

  function updateDates(cam_id, _date, _dir, _type)
  {
    for (var i = 0; i < images[cam_id].length; i++)
    {
      images[cam_id][i].src = "";
    }

    $.ajax({
      type: "GET",
      url: "api/pictures",
      data: { format: 'json', camera: cam_id, date: _date.toISOString(), dir: _dir, type: _type },
      success: function(response)
      {
        console.log("executed: " + response);
        addImages(cam_id, response);
      }
    });

    $.ajax({
      type: "GET",
      url: "api/statistics",
      data: { format: 'json', camera: cam_id, type: _type },
      success: function(response)
      {
        document.getElementById("cam" + cam_id + "_info3").innerHTML = "Data <b>" + response["data_month"] + "</b> Mt (kk), <b>" + response["data_day"] + "</b> Mt (vrk)";
        document.getElementById("cam" + cam_id + "_info4").innerHTML = "Kuvia <b>" + response["pics_month"] + "</b> (kk), <b>" + response["pics_day"] + "</b> (vrk)";
      }
    });

    $.getJSON(static_loc + "data/vars.json", function(data)
    {
      days = Math.floor(data["cam" + cam_id]["uptime"] / 86400);
      hours = Math.floor((data["cam" + cam_id]["uptime"] % 86400) / 3600);
      document.getElementById("cam" + cam_id + "_info1").innerHTML = "Käynnissä <b>" + days + "</b> päivää, <b>" + hours + "</b> tuntia";
      document.getElementById("cam" + cam_id + "_info2").innerHTML = "Viimeisin <b>" + data["cam" + cam_id]["last_heard"] + "</b>";
    });
  }

  function addZero(i)
  {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
  }

  function convertIncomingDate(date)
  {
    new_date = new Date(date);
    //console.log("converting date: " + date + " -> " + new_date);
    return new_date;
    //return new Date(date.getTime() + date.getTimezoneOffset()*60*1000);
  }

  function addImages(cam_id, data)
  {
    images[cam_id] = data;
    current_idx[cam_id] = -1;

    var old_tbody = document.getElementById("cam" + cam_id + "_select").tBodies[0];
    var new_tbody = document.createElement('tbody');

    if (images[cam_id].length != 0)
    {
      for (var i = 0; i < images[cam_id].length; i++)
      {
        var row = new_tbody.insertRow(i);
        var cell = row.insertCell(0);
        var innerDiv = document.createElement('div');

        innerDiv.setAttribute("onmouseover", "anim_image(\"" + cam_id + "\"," + i + ")");
        innerDiv.setAttribute("id", "cam" + cam_id + "_txt_" + i);
        innerDiv.setAttribute("style", "color: rgb(0, 0, 255); cursor: pointer; display: flex");

        date = convertIncomingDate(images[cam_id][i]['timestamp']);

        date_contents = date.getDate() + "." + (date.getMonth()+1) + " " + addZero(date.getHours()) + ":" + addZero(date.getMinutes())
        status_contents = '&nbsp;<img src="' + static_loc + 'loading.gif">'

        date_div = document.createElement('div');
        date_div.setAttribute("style", "flex-grow: 1");
        date_div.innerHTML = date_contents;
        innerDiv.appendChild(date_div);

        status_div = document.createElement('div');
        status_div.setAttribute("style", "flex-grow: 1");
        status_div.innerHTML = status_contents;
        innerDiv.appendChild(status_div);

        cell.appendChild(innerDiv);

        // preload
        preload_img[cam_id][i] = new Image();
        preload_img[cam_id][i].src = static_loc + images[cam_id][i]['filelocation'];
        preload_img[cam_id][i].my_id = i
        preload_img[cam_id][i].addEventListener("load", function(event)
        {
          var target = event.target || event.srcElement;
          var div = document.getElementById("cam" + cam_id + "_txt_" + target.my_id).getElementsByTagName('div');
          div[1].innerHTML = '&nbsp;<img src="' + static_loc + 'ready.gif"></div>'
        });
      }

      last_valid_start[cam_id] = convertIncomingDate(images[cam_id][0]['timestamp']);
      last_valid_end[cam_id] = convertIncomingDate(images[cam_id][images[cam_id].length - 1]['timestamp']);
      document.getElementById("cam" + cam_id + "_timespan").innerHTML =
        addZero(last_valid_start[cam_id].getHours()) + ":" + addZero(last_valid_start[cam_id].getMinutes()) + " - " +
        addZero(last_valid_end[cam_id].getHours()) + ":" + addZero(last_valid_end[cam_id].getMinutes());
    }
    else
    {
      var row = new_tbody.insertRow(i);
      var cell = row.insertCell(0);
      var innerDiv = document.createElement('div');
      innerDiv.innerHTML = "ajanjaksolle ei löydy kuvia";
      cell.appendChild(innerDiv);
      document.getElementById(cam + "_timespan").innerHTML = "-";
    }

    old_tbody.parentNode.replaceChild(new_tbody, old_tbody);

    if (images[cam_id].length != 0)
    {
      anim_image(cam_id, images[cam_id].length - 1);
    }
  }

  // Adds a header row to the table and returns the set of columns.
  // Need to do union of keys from all records as some records may not contain
  // all records
  function addAllColumnHeaders(data, selector)
  {
    var columnSet = [];
    var headerTr$ = $('<tr/>');

    for (var i = 0 ; i < data.length ; i++) {
      var rowHash = data[i];
      for (var key in rowHash) {
        if ($.inArray(key, columnSet) == -1){
          columnSet.push(key);
          headerTr$.append($('<th/>').html(key));
        }
      }
    }
    $(selector).append(headerTr$);

    return columnSet;
  }

  // Builds the HTML Table out of data
  function buildHtmlTable(data, selector)
  {
    var columns = addAllColumnHeaders(data, selector);

    for (var i = 0 ; i < data.length ; i++) {
      var row$ = $('<tr/>');
      for (var colIndex = 0 ; colIndex < columns.length ; colIndex++) {
        var cellValue = data[i][columns[colIndex]];

        if (cellValue == null)
        {
          cellValue = "";
        }
        else if (colIndex == 0)
        {
          var aTag = $('<a>', {href: 'movement?start=' + cellValue});
          aTag.text(cellValue);
          cellValue = aTag;
        }

        row$.append($('<td/>').html(cellValue));
      }

      $(selector).append(row$);
    }
  }
