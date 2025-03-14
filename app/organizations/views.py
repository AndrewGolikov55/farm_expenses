from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organization, Membership, Invitation
from .forms import OrganizationForm, InviteForm
from django.contrib.auth.models import User

@login_required
def org_list_view(request):
    memberships = Membership.objects.filter(user=request.user)
    if not memberships.exists():
        # Пользователь не в организации — найдём все приглашения 
        # (accepted=False, declined=False) для текущего email
        invites = Invitation.objects.filter(
            email=request.user.email,
            accepted=False,
            declined=False
        )
        return render(request, 'organizations/no_organization.html', {
            'invites': invites
        })

    # Если есть membership, редирект на единственную org_detail
    membership = memberships.first()
    return redirect('org_detail', org_id=membership.organization.id)


@login_required
def create_organization_view(request):
    """Создание новой организации (и назначение создателя админом)."""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save(commit=False)
            org.owner = request.user
            org.save()
            # Создать Membership для создателя (роль admin)
            Membership.objects.create(
                user=request.user,
                organization=org,
                role='admin'
            )
            messages.success(request, 'Организация создана!')
            return redirect('org_list')
    else:
        form = OrganizationForm()
    return render(request, 'organizations/create_org.html', {'form': form})


@login_required
def invite_user_view(request, org_id):
    org = get_object_or_404(Organization, id=org_id)

    # Проверяем, что текущий юзер - администратор данной организации
    membership = Membership.objects.filter(
        user=request.user,
        organization=org,
        role='admin'
    ).first()
    if not membership:
        messages.error(request, 'У Вас нет прав приглашать пользователей в эту организацию.')
        return redirect('org_list')

    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # **Проверка**: пользователь с таким email уже состоит?
            # Допустим, Вы определяете уникальный email = user.email
            # Тогда ищем Membership, у которого user.email == email
            already_member = Membership.objects.filter(
                user__email=email,
                organization=org
            ).exists()

            if already_member:
                messages.info(request, f'Пользователь с email {email} уже состоит в организации.')
                return redirect('org_detail', org_id=org.id)

            # Если не состоит, смотрим нет ли старых приглашений (optional)
            old_pending = Invitation.objects.filter(
                organization=org,
                email=email,
                accepted=False,
                declined=False
            )
            for old in old_pending:
                old.declined = True
                old.save()

            # Создаём новое приглашение
            Invitation.objects.create(
                organization=org,
                email=email
            )
            messages.success(request, f'Приглашение для {email} отправлено.')
            return redirect('org_detail', org_id=org.id)
    else:
        form = InviteForm()

    return render(request, 'organizations/invite.html', {'form': form, 'org': org})


@login_required
def org_leave_view(request, org_id):
    """Пользователь покидает организацию (удаляется его Membership)."""
    org = get_object_or_404(Organization, id=org_id)

    # Найдём Membership
    membership = Membership.objects.filter(user=request.user, organization=org).first()
    if not membership:
        messages.error(request, 'Вы не состоите в этой организации или уже вышли из неё.')
        return redirect('org_list')

    # (Дополнительно можно проверить, что если user - единственный админ,
    #  то не позволять выходить, пока не назначен новый админ. Но это уже
    #  бизнес-логика на Ваше усмотрение.)

    membership.delete()
    messages.success(request, f'Вы покинули организацию: {org.name}')

    return redirect('org_list')


@login_required
def confirm_invitation_view(request, token):
    inv = get_object_or_404(Invitation, token=token, accepted=False)

    # Сравниваем email текущего пользователя
    if request.user.email != inv.email:
        messages.error(request, 'Этот токен приглашения не принадлежит Вашему пользователю.')
        return redirect('org_list')

    # Создаём Membership (если ещё не существует)
    Membership.objects.get_or_create(
        user=request.user,
        organization=inv.organization,
        defaults={'role': 'member'}
    )
    inv.accepted = True
    inv.save()

    messages.success(request, f'Вы присоединились к организации {inv.organization.name}!')
    return redirect('org_list')


@login_required
def decline_invitation_view(request, token):
    """Пользователь отклоняет приглашение."""
    inv = get_object_or_404(Invitation, token=token, accepted=False, declined=False)
    
    # Убедимся, что email совпадает
    if request.user.email != inv.email:
        messages.error(request, 'Этот токен приглашения не принадлежит Вашему пользователю.')
        return redirect('org_list')

    inv.declined = True
    inv.save()

    messages.success(request, 'Приглашение отклонено.')
    return redirect('org_list')


@login_required
def org_detail_view(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    membership = Membership.objects.filter(user=request.user, organization=org).first()
    if not membership:
        messages.error(request, "У Вас нет доступа к этой организации.")
        return redirect('org_list')

    # Список участников
    members = Membership.objects.filter(organization=org)

    # Показываем приглашения только админу
    invitations = []
    if membership.role == 'admin':
        invitations = Invitation.objects.filter(organization=org)

    context = {
        'org': org,
        'membership': membership,
        'members': members,
        'invitations': invitations,
    }
    return render(request, 'organizations/org_detail.html', context)
