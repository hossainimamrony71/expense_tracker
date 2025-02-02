from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework import viewsets,filters
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import  api_view, permission_classes, action
from account.permissions import IsAdmin
from account.models import User
from .permissions import IsOwnerOrReadOnly, IsDepartmentUser,IsOwnerOrReadOnlyTransaction
from .models import Transaction, ExpenceCategory, LoanRequest
from .serializers import TransactionSerializer, ExpenceCategorySerializer,UserAllocatedSerializer, LoanRequestSerializer, AdminAllocatedSerializer
from django.db.models import Q
from django.core.exceptions import ValidationError
from .filters import TransactionFilter
from django_filters.rest_framework import DjangoFilterBackend


@api_view(["POST"])
@permission_classes([IsAdmin])
def user_allocated_money(request, *args, **kwargs):
    serializer = UserAllocatedSerializer(data=request.data, context={'request': request})
    if serializer.is_valid(raise_exception=True):
        ammount = serializer.validated_data["ammount"]
        source = serializer.validated_data["source"]
        recipient = serializer.validated_data['user']
        created_at = serializer.validated_data.get('created_at', timezone.now())
        admin_user = request.user
        if admin_user.balance < ammount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin_user.balance -= ammount
        admin_user.save()
        
        recipient.balance += ammount
        recipient.save()
        
        Transaction.objects.create(
            user = admin_user,
            ammount = ammount,
            source = source,
            transaction_type = "user_allocated_money",
            created_at=created_at,
       
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAdmin])
def admin_allocated_money(request, *args, **kwargs):
    serializer = AdminAllocatedSerializer(data=request.data, context={'request': request})
    if serializer.is_valid(raise_exception=True):
        ammount = serializer.validated_data["ammount"]
        source = serializer.validated_data["source"]
        created_at = serializer.validated_data.get('created_at', timezone.now())
        admin_user = request.user
        admin_user.balance += ammount
        admin_user.save()
        Transaction.objects.create(
            user = admin_user,
            ammount = ammount,
            source = source,
            transaction_type = "admin_allocated_money",
            created_at=created_at,
       
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       

class ExpenceCategroyViewset(viewsets.ModelViewSet):
    serializer_class = ExpenceCategorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = ExpenceCategory.objects.all()
    
    def get_queryset(self):
        if self.request.user.user_type == "admin":
            return ExpenceCategory.objects.all()
        return ExpenceCategory.objects.filter(creted_by = self.request.user).distinct()
    
    def perform_create(self, serializer):
        serializer.save(creted_by = self.request.user)
    
    def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Expense category deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    
class TransactionViewset(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyTransaction]
    queryset = Transaction.objects.all()
    
        # **Filter Backends**
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter

    # **Search Fields**
    search_fields = ['transaction_type', 'category__name', 'user__username', 'user__user_type', 'source']

    # **Ordering Fields**
    ordering_fields = ['created_at', 'ammount', 'category__name']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        if self.request.user.user_type == "admin":
            return Transaction.objects.all()
        return Transaction.objects.filter(user = self.request.user).distinct()
    
    def perform_create(self, serializer,partial=False):
        user = self.request.user 
        ammount = serializer.validated_data['ammount']
        if ammount>user.balance:
            raise serializers.ValidationError({"error": "Insufficient Balance!"})
        
        user.balance -= ammount
        user.save()
        serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        # Safely get 'amount' if it's provided; default to None
        new_amount = serializer.validated_data.get('ammount', None)
        old_amount = serializer.instance.ammount

        if new_amount is not None:
            # Calculate the difference between new and old amounts
            amount_difference = new_amount - old_amount

            if amount_difference > 0 and amount_difference > user.balance:
                raise serializers.ValidationError({"error": "Insufficient Balance!"})

            # Update the user's balance
            user.balance -= amount_difference
            user.save()

        # Proceed to save the updated transaction
        serializer.save(user=user)
    
        

class LoanRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LoanRequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = LoanRequest.objects.all()
    
    def get_permissions(self):
        if self.action in ['approve_loan', 'decline_loan']:
            permission_classes = [IsAuthenticated, IsAdmin]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsDepartmentUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user 
        if user.user_type == 'admin':
            return LoanRequest.objects.all()
        elif user.user_type in ['ted', 's2l']:
            return LoanRequest.objects.filter(
                Q(from_department = user.user_type) | Q(to_department = user.user_type)
            )
        else:
            return LoanRequest.objects.none() 
    

        
    def perform_create(self, serializer):
        user = self.request.user
        from_department = user.user_type
        to_department = serializer.validated_data.get("to_department")

        if to_department == from_department:
            raise serializers.ValidationError({"Error": "Cannot request a loan from the same department."})
        serializer.save(from_department=from_department) 
        
    def perform_update(self, serializer):
        user = self.request.user
        from_department = user.user_type
        to_department = serializer.validated_data.get("to_department")
        if to_department == from_department:
            raise serializers.ValidationError({"Error": "Cannot request a loan from the same department."})
        try:
            serializer.save()
        except ValidationError as e:
            raise serializers.ValidationError({"Error": str(e)})
        
    @action(detail=True, methods=['POST'], permission_classes = [IsAuthenticated, IsAdmin])
    def approve_loan(self, request, pk=None):
        loan_request = self.get_object()
        try:
            loan_request.approve(user=request.user)
            return Response({"message": "Loan  Approved!"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated, IsAdmin])
    def decline_loan(self, request, pk=None):
        loan_request = self.get_object()
        try:
            loan_request.decline(user=request.user)
            return Response({"message": "Loan Declined!"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
        
        
        
        