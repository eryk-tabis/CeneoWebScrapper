from wtforms import Form, StringField, ValidationError, validators, SubmitField
import requests
class InputForm(Form):
    product_id = StringField('Id produktu', validators=[validators.InputRequired()], render_kw={"placeholder": "Podaj id produktu"})
    submit = SubmitField(label='Potwierdź')
    def validate_product_id(form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError('Id produktu musi być liczbą')
        if requests.get(f'https://www.ceneo.pl/{field.data}').status_code == 404:
            raise ValidationError(f'Nie znaleziono produktu o id {field.data}')
