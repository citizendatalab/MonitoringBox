(function ($) {
  jQuery(document).ready(function ($) {
    $(".dynamicTable[data-ajax-endpoint]").each(function (i, v) {

      function createTable(tableWrapper) {
        var classes = "";
        var classesThead = "";
        if ($(tableWrapper).attr("data-classes")) {
          classes = " class=\"" + $(tableWrapper).attr("data-classes") + "\"";
        }
        if ($(tableWrapper).attr("data-classes-thead")) {
          classesThead = " class=\"" + $(tableWrapper).attr("data-classes-thead") + "\"";
        }
        $(tableWrapper).html(
          "<div class=\"table-options\"><div class=\"dropdown results-per-page\"><button class=\"btn btn-light btn-outline-secondary btn-sm dropdown-toggle\" type=\"button\" id=\"dropdownMenuButton\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"/><div class=\"dropdown-menu\" aria-labelledby=\"dropdownMenuButton\"></div></div><div class=\"ajaxPagination\"></div></div><table" + classes + "><thead" + classesThead + "></head><tbody></tbody></table><div class=\"table-options\"><div class=\"dropdown results-per-page\"><button class=\"btn btn-light btn-outline-secondary btn-sm dropdown-toggle\" type=\"button\" id=\"dropdownMenuButton\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"false\"/><div class=\"dropdown-menu\" aria-labelledby=\"dropdownMenuButton\"></div></div><div class=\"ajaxPagination\"></div></div>");
      }

      function generateHeading(data) {
        if (data["order_setable"]) {
          return "<th>" + data["name"] + "<i class=\"fa fa-sort-" + data["order"] + "\" aria-hidden=\"true\"></i></th>";
        }
        else {
          return "<th>" + data["name"] + "</th>";
        }
      }

      function generateRow(data) {
        return "<tr><td>" + data.join("</td><td>") + "</td></tr>";
      }

      function getRequestData(tableWrapper) {
        var data = {};
        if ($(tableWrapper).attr("data-ajaxdata-per-page")) {
          data["per_page"] = $(tableWrapper).attr("data-ajaxdata-per-page");
        }
        if ($(tableWrapper).attr("data-ajaxdata-start")) {
          data["start"] = $(tableWrapper).attr("data-ajaxdata-start");
        }
        return data;
      }

      function generatePaginationLi(url, text, linkAttr = "", classes = "page-item") {
        linkAttr = linkAttr == "" ? linkAttr : " " + linkAttr;
        return "<li class=\"" + classes + "\"><a class=\"page-link\" href=\"" + url + "\"" + linkAttr + ">" + text + "</a></li>";
      }

      function generatePagination(info) {
        var pageCountRange = 5;
        var out = "<nav aria-label=\"Page navigation\"><ul class=\"pagination pagination-sm\">";
        //Prev
        if (info["current_start"] != 0) {
          out += generatePaginationLi("#",
            "<span aria-hidden=\"true\">&laquo;</span><span class=\"sr-only\">Previous</span>",
            " aria-label=\"Previous\" data-page=\"0\"");
        }

        var pageCount = info["count_total"] / info["per_page"];
        var current_page = info["current_start"] / info["per_page"];
        var pageStart = Math.max(0, current_page - pageCountRange);
        var page = info["per_page"] * pageStart;

        for (var i = pageStart; i < Math.min(pageCount, current_page + pageCountRange); i++) {
          out += generatePaginationLi("#",
            (i + 1) + (i == current_page ? "<span class=\"sr-only\">(current)</span>" : ""),
            " data-page=\"" + page + "\"", i == current_page ? "page-item active" : "page-item");
          page += info["per_page"];
        }


        // Next
        if (current_page + 1 < pageCount) {
          out += generatePaginationLi("#",
            "<span aria-hidden=\"true\">&raquo;</span><span class=\"sr-only\">Next</span>",
            " aria-label=\"Next\" data-page=\"" + ((current_page + 1 ) * info["per_page"]) + "\"");
        }


        return out + "</ul></nav>";
      }

      function updateContent(tableWrapper, url) {
        var data = getRequestData(tableWrapper);
        $.ajax({
          dataType: "json",
          url: url,
          data: data,
          success: function (data) {

            if (!$(tableWrapper).find("table").length) {
              createTable(tableWrapper);
            }
            if (data["info"]["show_heading"]) {
              $(tableWrapper).find(".table-options").show(0);
              var headings = "";
              for (var i in data["headers"]) {
                headings += generateHeading(data["headers"][i]);
              }
              $(tableWrapper).find("table thead").html(headings);
            }
            else {
              $(tableWrapper).find(".table-options").hide(0);
            }

            $(tableWrapper).find(".dropdown-menu").each(function () {
              if (data["info"]["possible_results_per_page"].length != $(this).find(".dropdown-item").length) {
                // regenerate all.
                var pagination = generatePagination(data["info"]);
                $(tableWrapper).find(".table-options .results-per-page").each(function (i, v) {
                  var possibleResultsPerPage = data["info"]["possible_results_per_page"];
                  var out = possibleResultsPerPage.join("</a><a class=\"dropdown-item\" href=\"#\">");

                  if (out !== "") {
                    out = "<a class=\"dropdown-item\" href=\"#\">" + out + "</a>";
                  }
                  $(v).find(".dropdown-menu").html(out);
                  $(v).find(".dropdown-item").click(function (e) {
                    e.preventDefault();
                    $(tableWrapper).attr("data-ajaxdata-per-page", $(this).text());
                    updateContent(tableWrapper, url);
                  });

                });

                $(tableWrapper).find(".ajaxPagination").each(function (i, v) {
                  $(v).html(pagination);
                  $(v).find("a").click(function (e) {
                    e.preventDefault();
                    $(tableWrapper).attr("data-ajaxdata-start", $(this).attr("data-page"));
                    updateContent(tableWrapper, url);
                  });
                });

              }
              else {
                // Check individual ones.
                for (var i = 0; i < data["info"]["possible_results_per_page"].length; i++) {
                  if ($($(this).find(".dropdown-item")[i]).html() != data["info"]["possible_results_per_page"][i]) {
                    $($(this).find(".dropdown-item")[i]).html(data["info"]["possible_results_per_page"][i]);
                  }
                }
              }
            });

            if ($(tableWrapper).attr("data-ajaxdata-per-page") != data["info"]["per_page"]) {
              $(tableWrapper).find("button.btn").html(data["info"]["per_page"]);
            }

            $(tableWrapper).attr("data-ajaxdata-per-page", data["info"]["per_page"]);
            $(tableWrapper).attr("data-ajaxdata-start", data["info"]["current_start"]);

            // Update table content.
            var trs = $(tableWrapper).find("table tbody tr");
            if (trs.length == data["body"].length) {
              for (var i in data["body"]) {
                var row = $(trs[i]).find("td");
                for (var k in data["body"][i]) {
                  if ($(row[k]).html() != data["body"][i][k]) {
                    $(row[k]).html(data["body"][i][k]);
                  }
                }
              }
              $(tableWrapper).find("table tbody").html(rows);
            }
            else {
              var rows = "";
              for (var i in data["body"]) {
                rows += generateRow(data["body"][i]);
              }
              $(tableWrapper).find("table tbody").html(rows);
            }
          }
        });

      }

      updateContent(v, $(v).attr("data-ajax-endpoint"));

      if ($(v).attr("data-ajax-refresh-time")) {
        setInterval(function () {
          updateContent(v, $(v).attr("data-ajax-endpoint"))
        }, $(v).attr("data-ajax-refresh-time"));
      }
    });
  });

  $("select[data-dynamic-description=\"true\"]").each(function (i, v) {
    function setDescription(select) {
      select.attr("aria-describedby", "description-" + select.val());
      select.parent().find(".descriptions>div").hide(0);
      select.parent().find(".descriptions div[data-description-for=\"" + select.val() + "\"]").fadeIn("slow");

    }

    setDescription($(this));

    $(this).change(function () {
      setDescription($(this));
    });

  });
  $('.modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var modalContentId = button.data('modal-content') // Extract info from data-* attributes
    if (modalContentId !== undefined) {
      var content = $(modalContentId);

      var modal = $(this)

      var modalContent = modal.find('.modal-content');
      modalContent.html(content);
      modalContent.trigger("modal.show", [{'button': button, 'modal': modal, 'event': event}]);
      modalContent.find("#modalRemoveRecordingVerification").show("fast");
    }

  });
  $('.modal-content').on('modal.show', function (event, params) {
    var button = $(params.button);
    var row = button.parent().parent().find("td")
    var name = $(row[0]).text();
    var mount = $(row[1]).text()
    var size = $(row[2]).text();
    $(params.modal).find('.data-name').html(name);
    $(params.modal).find('.data-mount').html(mount);
    $(params.modal).find('.data-size').html(size);
    $(params.modal).find('#submitter').attr('href', button.attr('data-action-url'));
  });

  $('.show-password').change(function () {
    var inputType = ['password', 'text'][1 * this.checked];
    $($(this).attr('data-password-to-show')).attr('type', inputType);
  });

  $('.charts').each(function (index, elemCharts) {
    var deviceId = $(elemCharts).attr("data-device");
    var chartContexts = {};
    var chartHandlers = {};
    setInterval(function () {
      $.ajax({
        dataType: "json",
        url: '/api/device/' + deviceId + '/live',
        success: function (data) {
          var createNew = $(elemCharts).find(".chart").length !== Object.keys(data).length;
          if (createNew) {
            // Create
            chartContexts = {};
            chartHandlers = {};
            var out = '<div class="container">';
            var i = 0;
            for (var k in data) {
              if (i % 2 == 0) {
                out += '<div class="row">';
              }
              out += '<div class="col"><div style="width:' + (($(
                  elemCharts).width() / 2) * 0.7) + 'px;" class="chart"><canvas id="chart[\'' + k + '\']" width="300" height="300"></canvas></div></div>';
              if (i % 2 == 1) {
                out += '</div>';
              }
              i++;
            }
            $(elemCharts).html(out + '</div>');
            for (var k in data) {
              chartContexts[k] = document.getElementById("chart['" + k + "']").getContext('2d');
              chartHandlers[k] = new Chart(chartContexts[k], {
                type: 'line',
                data: {
                  labels: ["1"],
                  datasets: [
                    {
                      label: k,
                      data: [0],
                      backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                      ],
                      borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                      ],
                      borderWidth: 1
                    }
                  ]
                },
                options: {
                  animation: {
                    duration: 0
                  },
                  scales: {
                    yAxes: [{
                      ticks: {
                        beginAtZero: false
                      }
                    }]
                  }
                }
              });

            }
          }
          for (var k in data) {
            while (data[k].length > chartHandlers[k].data.labels.length) {
              chartHandlers[k].data.labels.push(chartHandlers[k].data.labels.length + 1);
            }
            chartHandlers[k].data.datasets[0].data = data[k];
            chartHandlers[k].update();
          }
        }
      });

    }, $(elemCharts).attr("data-speed"));
    $(window).resize(function () {
      $(elemCharts).find(".chart").each(function (k, elem) {
        $(elem).width($(elem).parent().width() - 20);
      });
    });
  });
})(jQuery);
