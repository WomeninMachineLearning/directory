$(document).ready(function() {
    function percentString(decimal) {
        return (decimal * 100).toFixed(0) + '%';
    }

    function drawPieChart(divId, nbProfiles, totProfiles, label, color1) {
        const array = [['Position', 'Entries in Repository'],
                        [label, nbProfiles],
                        ['Rest', totProfiles - nbProfiles]
                     ];
        const data = google.visualization.arrayToDataTable(array);

        const options = {
            colors: ['#dedede', '#dedede'],
            fontName: 'Open Sans',
            fontSize: 14,
            chartArea: { left: '10%', top: 0, width: '80%', height: '100%' },
            width: 120,
            height: 120,
            legend: 'none',
            pieSliceText: 'none',
            pieHole: 0.6,
            enableInteractivity: false,
            slices: [{ color: color1, textStyle: { color: '#555555', fontName: 'Open Sans', fontSize: 18 } },
            { textStyle: { color: '#ffffff', fontName: 'Open Sans', fontSize: 1 } }]
        };

        const Piechart = new google.visualization.PieChart(document.getElementById(divId));

        Piechart.draw(data, options);
    }

    function preparePiecharts(positionsData) {
        const profRe = /lecturer|professor/i;
        const seniorRe = /senior|director/i;
        const studentRe = /student|resident/i;

        let totProfiles = 0;
        const profiles = {
            'prof': 0,
            'senior': 0,
            'student': 0,
            'other': 0
        }

        for (let i=0; i<positionsData.length; i++) {
            const pos = positionsData[i];
            totProfiles += pos.profiles_count;
            if (pos.position.match(seniorRe)) {
                profiles.senior += pos.profiles_count;
            }
            else if (pos.position.match(profRe)) {
                profiles.prof += pos.profiles_count;
            }
            else if (pos.position.match(studentRe)) {
                profiles.student += pos.profiles_count;
            }
            else {
                profiles.other += pos.profiles_count;
            }
        };

        $('#student-percent').text(percentString(profiles.student / totProfiles));
        $('#prof-percent').text(percentString(profiles.prof / totProfiles));
        $('#senior-percent').text(percentString(profiles.senior / totProfiles));
        $('#other-percent').text(percentString(profiles.other / totProfiles));

        $('#student-count').text(profiles.student + ' profiles');
        $('#prof-count').text(profiles.prof + ' profiles');
        $('#senior-count').text(profiles.senior + ' profiles');
        $('#other-count').text(profiles.other + ' profiles');

        $('#entries-number').text(totProfiles);

        drawPieChart('chartStudent', profiles.student, totProfiles, 'Students', '#e8a861');
        drawPieChart('chartOther', profiles.other, totProfiles, 'mid-career', '#e8a861');
        drawPieChart('chartProf', profiles.prof, totProfiles, 'Senior academic', '#e8a861');
        drawPieChart('chartSenior', profiles.senior, totProfiles, 'Other senior positions', '#e8a861');
    }

    function drawMap(divId, jsonData) {
        const array = jsonData.map(function(country) { return [country.name, country.profiles_count]; });
        array.unshift(['Country', 'Profiles']);

        const data = google.visualization.arrayToDataTable(array);

        const options = {
            colorAxis: { colors: ['#a2ccfc', '#3f4f61'] },
            legend: 'none',
            tooltip: { isHtml: false },
        };

        const chart = new google.visualization.GeoChart(document.getElementById(divId));
        chart.draw(data, options);
    }

    function init() {
        $.get('/api/countries/?format=json', function(data) { return drawMap('regions_div', data); });
        $.get('/api/positions/?format=json', function(data) { return preparePiecharts(data); });
    }

    google.charts.load('current', { 'packages': ['corechart', 'geochart'], 'mapsApiKey': 'AIzaSyCoD-FXcgIKxspIjalcutPYjaSK1B1WmXc' });
    google.charts.setOnLoadCallback(init);

    //create trigger to resizeEnd event
    $(window).resize(function () {
        if (this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function () {
            $(this).trigger('resizeEnd');
        }, 500);
    });

    //redraw graph when window resize is completed
    $(window).on('resizeEnd', function () {
        $.get('/api/countries/?format=json', function (data) { return drawMap('regions_div', data); });
    });
});
