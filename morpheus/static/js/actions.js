(function ($) {
	$('#submitButton').click(function(event) {

		func = $('#algo').val();
		console.log(func);

		data = $('#inData').val();
		console.log(data);

		$.ajax({
			type: 'GET',
			url: '/submit',
			data: {
				'function': func,
				'data': data,
			},
			error: function(err) {
				console.log(err);
			},
			success: function(data) {
				console.log(data['job_id']);
				alert('Job ID: ' + data['job_id']);
			}
		});

	});

	$('#testButton').click(function(event) {

		$.ajax({
			type: 'GET',
			url: '/available',
			error: function(err) {
				console.log(err);
			},
			success: function(data) {
				console.log(data);
			}
		});

	});

	$('#jobCheck').click(function(event) {

		job_id = $('#job_id').val();

		$.ajax({
			url: '/status',
			data: {
				job_id: job_id,
			},
			error: function(err) {
				console.log(err);
			},
			success: function(data) {
				console.log(data['status']);
				if (!data['status']) {
					$('#jobResult').text("not done");
				} else {
					$('#jobResult').text("done");
				}
			}
		});

	});

})(jQuery);
