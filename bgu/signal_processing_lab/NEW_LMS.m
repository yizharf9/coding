function [Wout, WConv, Er, Rout] = NEW_LMS(Win, InSig, RefSig, U, R, dN)
%     Newton LMS adaptive algorithm
%     ---------------------------------------
% Input :
%--------
% Win - Starting weights (column vector)
% InSig - input signal   (for multi inputs inSig is an array)
% RefSig - refference signals (Desired respomse)
% U - convergence rate
% R - correlation matrix of input InSig
% dN - Rate of estimation of R (if not given)
%
% Output :
%---------
% Wout - Output weights
% WConv - convergence of weights
% Er - error signal
% Rout - last correlation matrix
%
clc
Wsize = size(Win);, if Wsize(1,2)~=1, error(' Win - should be a column vector'), end
Wsize = max(Wsize);

[C, Ln] = size(InSig);, if C~=1 & C~=Wsize, error(' InSig - should be a row vector'), end
MultiRef = 0;
if C==Wsize, MultiRef = 1;, end

[Rc, Rr] = size(RefSig);
if Rc~=1, error(' RefSig - wrong number of columns'), end
if Rr~=Ln, error(' RefSig - should be in the length of InSig'), end

Esti = 0;
[Rc, Rr] = size(R);
if Rc==0 & Rr==0,
  if dN<1, error(' dN - have wrong value'), end
  R_1 = zeros(Wsize);
  Rt = zeros(Wsize);
  Esti = 1;
elseif Rc~=Rr | Rc~=Wsize,
  error(' R matrix dimention are worng')
else
  R_1 = inv(R);
end

Wout = Win;
WConv = zeros(Wsize, Ln);
Er = zeros(1, Ln);

for a=1:Ln
  if MultiRef,
    Sig = InSig(:,a);
  else
    if a<Wsize,
      Sig = zeros(Wsize, 1);
      Sig(1:a) = InSig(a:-1:1);
    else
      Sig = InSig(a:-1:(a-Wsize+1))';
    end
  end

  Out = Wout' * Sig;

  Er(a:a) = RefSig(a:a) - Out;

  if Esti,
     Rt = Rt + Sig * Sig';
     if a-floor(a/dN)*dN==0,
       Rt = Rt ./ dN;
       home
       a
       Rt1 = toeplitz(Rt(1,:),Rt(1,:))
       R_1 = inv(Rt1);
       Rt1=[];
       Rt = zeros(Wsize);
     end
  end

  Wout = Wout + U * 2 * Er(a:a) * R_1 * Sig ;
  WConv(:,a) = Wout ;

end, %next a
Rout = inv(R_1);

end