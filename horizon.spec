%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define py_puresitedir  %{python_sitelib}
%define httpd_conf /etc/httpd/conf/httpd.conf

Name:           horizon
Version:        2012.1
Release:        1%{?dist}
Url:            http://www.openstack.org
License:        Apache 2.0
Source0:        %{name}-%{version}.tar.gz  
BuildRoot:      %{_tmppath}/%{name}-%{version}
BuildRequires:  python-devel python-setuptools python-sphinx
BuildArch:      noarch

Group:          Development/Languages/Python
Summary:        A Django module for OpenStack
Requires:       python-novaclient python-keystoneclient openstackx python-cloudfiles
Requires:       python-dateutil python-eventlet >= 0.9.12 python-greenlet >= 0.3.1
Requires:       python-sqlalchemy >= 0.6.3 python-sqlalchemy-migrate >= 0.6
Requires:       python-httplib2
Requires:       Django >= 1.3 django-nose

%description
The OpenStack Dashboard is a reference implementation of a Django site that
uses the Django-Nova project to provide web based interactions with the
OpenStack Nova cloud controller.


%package -n openstack-dashboard
Group:          Development/Languages/Python
Summary:        Django based reference implementation of a web based management interface for OpenStack.
Requires:       horizon = %{version}-%{release} httpd mod_wsgi memcached python-memcached


%description -n openstack-dashboard
The Horizon project is a Django module that is used to provide web based
interactions with an OpenStack cloud.

There is a reference implementation that uses this module located at:

    http://launchpad.net/horizon

It is highly recommended that you make use of this reference implementation
so that changes you make can be visualized effectively and are consistent.
Using this reference implementation as a development environment will greatly
simplify development of the horizon module.

Of course, if you are developing your own Django site using Horizon, then
you can disregard this advice.


%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}


%description doc
Documentation for %{name}.


%prep
%setup -q -n %{name}-%{version}
sed -i "s|'/auth/logout'|'%s/auth/logout' % request.environ.get('SCRIPT_NAME', '')|" horizon/horizon/middleware.py


%build
cd horizon
%__rm -rf horizon/tests
%{__python} setup.py build

cd ../openstack-dashboard
sed -i "s|sys.path.append(ROOT_PATH)|sys.path.append(ROOT_PATH); sys.path.append('/etc/openstack-dashboard')|" dashboard/settings.py
(cd local && mv local_settings.py.example local_settings.py)

%{__python} setup.py build


%install
%__rm -rf %{buildroot}
cd horizon

%{__python} setup.py install  -O1 --skip-build --root=%{buildroot}
cp -a horizon/locale %{buildroot}%{python_sitelib}/horizon

cd ../openstack-dashboard
cp -a dashboard %{buildroot}%{python_sitelib}/dashboard

cd ..
DASHBOARD_CONFDIR=%{buildroot}%{_sysconfdir}/openstack-dashboard/local
install -d -m 755 "$DASHBOARD_CONFDIR"
install -m 644 redhat/local_settings.py "$DASHBOARD_CONFDIR"
touch "$DASHBOARD_CONFDIR"/__init__.py

install -d -m 755 %{buildroot}%{_localstatedir}/lib/openstack-dashboard
install -d -m 755 %{buildroot}%{_localstatedir}/log/openstack-dashboard
install -D -m 644 redhat/openstack-dashboard.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/openstack-dashboard.conf

# TODO: deal with quantum sphinx complains on
make -C docs html PYTHONPATH=%{buildroot}%{python_sitelib}


%clean
%__rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc horizon/README
%{python_sitelib}/horizon*


%files -n openstack-dashboard
%defattr(-,root,root,-)
%doc openstack-dashboard/README
%dir %attr(0755, apache, apache) %{_localstatedir}/lib/openstack-dashboard
%dir %attr(0755, apache, apache) %{_localstatedir}/log/openstack-dashboard
%{python_sitelib}/dashboard*
%{_sysconfdir}/httpd/conf.d/*
%{_sysconfdir}/openstack-dashboard
%config(noreplace) %{_sysconfdir}/openstack-dashboard/local/*py


%files doc
%defattr(-,root,root,-)
%doc docs/build/html


%changelog
* Wed Jan 05 2012 Alessio Ababilov <aababilov@griddynamics.com> - 2012.1
- Initial release: spec created
