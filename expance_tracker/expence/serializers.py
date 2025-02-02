from rest_framework import serializers
from .models import Transaction, ExpenceCategory, LoanRequest


class AdminAllocatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'ammount', 'created_at', 'source')

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user.user_type != 'admin':
            raise serializers.ValidationError("Only admins can perform this action.")
        return data


class UserAllocatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'ammount', 'created_at', 'source', 'user')

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user.user_type != 'admin':
            raise serializers.ValidationError("Only admins can perform this action.")
        return data


class ExpenceCategorySerializer(serializers.ModelSerializer):
    creted_by = serializers.ReadOnlyField(source='created_by.username')  
    class Meta:
        model = ExpenceCategory
        fields = "__all__"
        
class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_type = serializers.ReadOnlyField(source='user.user_type')
    category = serializers.PrimaryKeyRelatedField(queryset=ExpenceCategory.objects.all())
    category_details = ExpenceCategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TransactionSerializer, self).__init__(*args, **kwargs)
        request_method = self.context.get('request').method if self.context.get('request') else None

        if request_method in ['PUT', 'PATCH']:
            # For updates, make all fields optional
            for field in self.fields.values():
                field.required = False




class LoanRequestSerializer(serializers.ModelSerializer):
    from_department_display = serializers.CharField(source='get_from_department_display', read_only=True)
    to_department_display = serializers.CharField(source='get_to_department_display', read_only=True)
    approved_by_username = serializers.CharField(source="approved_by.username", read_only=True)
    
    class Meta:
        model = LoanRequest
        fields = [
            'id', 'from_department_display', 'to_department', 'to_department_display', 'amount', 'status', 'approved_at', 'approved_by', 'approved_by_username'
        ]
        read_only_fields = ['status', 'requested_at', 'approved_by', 'approved_by_username']

    def validate(self, attrs):
        to_department = attrs.get('to_department')
        from_department = self.context['request'].user.user_type  # the requesting user's department

        if from_department == to_department:
            raise serializers.ValidationError("Cannot request a loan from the same department.")
        
        if from_department not in ['ted', 's2l'] or to_department not in ['ted', 's2l']:
            raise serializers.ValidationError("Invalid department selection.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['from_department'] = user.user_type
        return super().create(validated_data)
