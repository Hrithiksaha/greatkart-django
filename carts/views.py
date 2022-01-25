from django.shortcuts import redirect, render , get_object_or_404
from store.models import Product 
from store.models import Variation
from carts.models import Cart,CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):
    cart=request.session.session_key

    if not cart:
        cart=request.session.create()
    
    return cart

def add_cart(request,product_id):
    current_user=request.user 
    product=Product.objects.get(id=product_id)

    #If user is autheticated:
    if current_user.is_authenticated:
        variation_list=[]

        if request.method ==  'POST' : 
            for item in request.POST:
                key=item 
                value=request.POST[key]

                try:
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    #print(variation)
                    variation_list.append(variation)
                except :
                    pass

        is_cart_item_exist=CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_item_exist:
            #check existing variation -->database
            #check current variation --> variation_list
            #item_id -->database 

            cart_item=CartItem.objects.filter(product=product,user=current_user)

            ex_var_list=[]
            id_list=[]

            for item in cart_item:
                existing_variation= item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)

            # print(ex_var_list)
            # print(item_id)

            if variation_list in ex_var_list:
                    #quantity increase by 1
                    index=ex_var_list.index(variation_list)
                    item_id=id_list[index]
                    item=CartItem.objects.get(product=product, id=item_id)
                    
                    item.quantity +=1 
                    item.save()

            else:
                    item=CartItem.objects.create(product=product,user=current_user,quantity=1)
                    if len(variation_list)>0:
                        item.variations.clear()
                        item.variations.add(*variation_list)
                    item.save()

        else :
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(variation_list)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*variation_list)
            cart_item.save()
        return redirect('cart')
        
    else:

        variation_list=[]

        if request.method ==  'POST' : 
            for item in request.POST:
                key=item 
                value=request.POST[key]

                try:
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    #print(variation)
                    variation_list.append(variation)
                except :
                    pass

        
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist :
            cart=Cart.objects.create(
                cart_id=_cart_id(request)

            )
        cart.save() 


        is_cart_item_exist=CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exist:
            #check existing variation -->database
            #check current variation --> variation_list
            #item_id -->database 

            cart_item=CartItem.objects.filter(product=product,cart=cart)

            ex_var_list=[]
            id_list=[]

            for item in cart_item:
                existing_variation= item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)

            # print(ex_var_list)
            # print(item_id)

            if variation_list in ex_var_list:
                    #quantity increase by 1
                    index=ex_var_list.index(variation_list)
                    item_id=id_list[index]
                    item=CartItem.objects.get(product=product, id=item_id)
                    
                    item.quantity +=1 
                    item.save()

            else:
                    item=CartItem.objects.create(product=product,cart=cart,quantity=1)
                    if len(variation_list)>0:
                        item.variations.clear()
                        item.variations.add(*variation_list)
                    item.save()

        else :
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(variation_list)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*variation_list)
            cart_item.save()
    

        return redirect('cart')


def remove_cart(request,product_id,cart_item_id):
        product=get_object_or_404(Product,id=product_id)
        
        try:
            if request.user.is_authenticated:
                cart_item=CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
            else:
                cart=Cart.objects.get(cart_id=_cart_id(request))

                cart_item=CartItem.objects.get(product=product,cart=cart, id=cart_item_id)

            if cart_item.quantity>1:
                cart_item.quantity-=1
                cart_item.save()

            else:
                cart_item.delete()
        except:
            pass
        
        return redirect('cart')


def delete_cart(request,product_id,cart_item_id):
    product=get_object_or_404(Product,id=product_id)
    
    
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)

        cart_item.delete()
    except:
        pass
    
    return redirect('cart')


def cart(request,total=0,quantity=0, carts_item=None):
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True) 
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True) 



        for cart_item in cart_items:
            total+=cart_item.product.price * cart_item.quantity
            quantity+=cart_item.quantity
        
        tax=(2*total)/100
        grand_total=total+tax

    except ObjectDoesNotExist:
        pass 

    context={
        'quantity':quantity,
        'total':total, 
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }

    return render(request,'store/cart.html',context)

@login_required(login_url='login')
def checkout(request,total=0,quantity=0, carts_item=None):
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True) 
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True) 
        # cart=Cart.objects.get(cart_id=_cart_id(request))
        # cart_items=CartItem.objects.filter(cart=cart,is_active=True) 

        for cart_item in cart_items:
            total+=cart_item.product.price * cart_item.quantity
            quantity+=cart_item.quantity
        
        tax=(2*total)/100
        grand_total=total+tax

    except ObjectDoesNotExist:
        pass 

    context={
        'quantity':quantity,
        'total':total, 
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/checkout.html',context)
