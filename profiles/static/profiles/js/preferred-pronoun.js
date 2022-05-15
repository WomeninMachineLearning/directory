window.onpaint = function() {
    $("#id_other_pronoun").hide();
};

(function() {
    $("#id_preferred_pronoun").change(function () {
        if($(this).val() == 'OTHER') {
            $("#id_other_pronoun").show();
        } else {
            $("#id_other_pronoun").hide();
        }
		
        return True
    });
    
}
)();