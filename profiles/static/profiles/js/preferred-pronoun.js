window.onload = function() {
    if($("#id_preferred_pronoun").val() != 'Other') {
        $("#id_other_pronoun").hide();
    }
};

(function() {
    $("#id_preferred_pronoun").change(function () {
        if($(this).val() == 'Other') {
            document.getElementById("id_other_pronoun").value = '';
            $("#id_other_pronoun").show();
        } else if($(this).val() == '') {
            $("#id_other_pronoun").hide();
            document.getElementById("id_other_pronoun").value = 'None';
        } else {
            $("#id_other_pronoun").hide();
            document.getElementById("id_other_pronoun").value = document.getElementById("id_preferred_pronoun").value;
        }
        return True
    }); 
}
)();